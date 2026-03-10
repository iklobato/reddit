# Camera Scanner with Tor Proxy

This project contains a camera scanner application that searches for IP cameras on a network and attempts to access them using RTSP URLs with various credentials. It can use a Tor proxy for anonymized scanning.

## Features

- Network scanning for IP cameras
- Testing various RTSP URLs and credentials
- Capturing frames from accessible cameras
- SQLite database storage for found cameras
- Tor proxy integration for anonymized scanning
- Docker-based deployment

## Files

- `t1.py`: Main camera scanner application
- `config.yaml`: Configuration for local execution
- `config-docker.yaml`: Configuration for Docker execution (uses Tor container)
- `usernames.txt`: List of usernames to try
- `passwords.txt`: List of passwords to try
- `Dockerfile`: Container definition for the scanner
- `docker-compose.yml`: Orchestration for both scanner and Tor
- `torrc`: Tor configuration file

## Docker Setup

1. Make sure Docker and Docker Compose are installed on your system
2. Customize the network range in `config-docker.yaml` to scan your target network
3. Build and start the containers:

```bash
docker-compose up -d
```

4. Check the logs:

```bash
docker-compose logs -f
```

5. Stop the containers:

```bash
docker-compose down
```

## Data Persistence

- Captured frames are stored in the `./frames` directory
- The camera database is stored in `./cameras.db`
- Logs are saved to `./scanner.log`

## Customization

- Edit `config-docker.yaml` to change:
  - Network range to scan
  - Ports to check
  - Username/password lists
  - RTSP URL patterns
  - Logging level
  - Scanning intervals

## Security Notes

- Using Tor for scanning adds a layer of anonymity but is not foolproof
- Be aware of legal implications when scanning networks you don't own
- This tool is intended for security research and legitimate network management 