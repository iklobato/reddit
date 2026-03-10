# Snak Specification V11

This document provides a comprehensive reference for the Snak Specification V11, including all object definitions, field types, requirements, allowed values, descriptions, and examples.

---

## Table of Contents
1. [Snak Object](#snak-object)
2. [snakFormat Object](#snakformat-object)
3. [snakVersion Object](#snakversion-object)
4. [controlbar Object](#controlbar-object)
5. [snakUrls Object](#snakurls-object)
6. [startBehaviour Format](#startbehaviour-format)
7. [endBehaviour Format](#endbehaviour-format)
8. [timeoutMessage Object](#timeoutmessage-object)
9. [imageMedia Object](#imagemedia-object)
10. [videoMedia Object](#videomedia-object)
11. [soundMedia Object](#soundmedia-object)
12. [background Object](#background-object)
13. [border Object](#border-object)
14. [font Object](#font-object)
15. [action Object](#action-object)
16. [animation Object](#animation-object)
17. [graphNodeElement Object](#graphnodeelement-object)
18. [ratingItem Object](#ratingitem-object)
19. [rankingItem Object](#rankingitem-object)
20. [tag Object](#tag-object)
21. [layer Object](#layer-object)
22. [timeline Object](#timeline-object)
23. [timelineItem Object](#timelineitem-object)
24. [node Object](#node-object)

---

## 1. Snak Object

| Field           | Type         | Required | Nullable | Allowed Values/Format | Description | Example |
|----------------|--------------|----------|----------|----------------------|-------------|---------|
| id             | uuid         | Yes      | No       | -                    | The ID of the Snak. | `"b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f"` |
| name           | string       | Yes      | No       | -                    | The name of the Snak. | `"My Snak"` |
| format         | snakFormat   | Yes      | No       | -                    | A 'snakFormat' object describing the Snak format. | See [snakFormat Object](#snakformat-object) |
| version        | snakVersion  | Yes      | No       | -                    | A 'snakVersion' object describing the Snak version. | See [snakVersion Object](#snakversion-object) |
| aspectRatio    | aspectRatio  | Yes      | No       | String, e.g. '6:9'   | The aspect ratio of the Snak. | `"16:9"` |
| previewUrl     | url          | Yes      | Yes      | -                    | URL to the preview image. If null, default preview is used. | `"https://example.com/preview.png"` |
| playButtonUrl  | url          | Yes      | Yes      | -                    | URL to the play button image. If null, default is used. | `"https://example.com/play.png"` |
| autoPlay       | boolean      | Yes      | No       | true/false           | If true, Snak auto-plays; if false, shows play button. | `true` |
| controlbar     | controlbar   | Yes      | No       | -                    | Player control bar configuration. | See [controlbar Object](#controlbar-object) |
| sessionTimeout | integer      | Yes      | No       | Milliseconds         | Time after last user interaction before replay button. 0 disables timeout. | `30000` |
| urls           | snakUrls     | Yes      | No       | -                    | URLs for loading content. | See [snakUrls Object](#snakurls-object) |
| themes         | array(theme) | Yes      | No       | -                    | Array of themes used by the Snak. | `["dark", "light"]` |
| timelines      | array(timeline) | Yes   | No       | -                    | Array of timeline objects. | See [timeline Object](#timeline-object) |

**Example:**
```json
{
  "id": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f",
  "name": "My Snak",
  "format": { "version": 11 },
  "version": { "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab", "number": 3 },
  "aspectRatio": "16:9",
  "previewUrl": "https://example.com/preview.png",
  "playButtonUrl": null,
  "autoPlay": true,
  "controlbar": { "show": true, ... },
  "sessionTimeout": 30000,
  "urls": { "staticContent": "https://cdn.example.com/", "font": null, "api": "https://api.example.com/" },
  "themes": ["dark", "light"],
  "timelines": [ ... ]
}
```

---

## 2. snakFormat Object

| Field   | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|---------|---------|----------|----------|----------------------|-------------|---------|
| version | integer | Yes      | No       | -                    | The version number of the Snak format. | `11` |

**Example:**
```json
{ "version": 11 }
```

---

## 3. snakVersion Object

| Field  | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|--------|--------|----------|----------|----------------------|-------------|---------|
| id     | uuid   | Yes      | No       | -                    | The ID of the version. | `"a1b2c3d4-5678-90ab-cdef-1234567890ab"` |
| number | int    | Yes      | No       | >= 1                 | The version number, starting at 1 and incrementing. | `3` |

**Example:**
```json
{ "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab", "number": 3 }
```

---

## 4. controlbar Object

| Field      | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|------------|---------|----------|----------|----------------------|-------------|---------|
| show       | boolean | Yes      | No       | true/false           | Show or hide the controlbar. | `true` |
| play       | object  | Yes      | No       | { show: boolean }    | Play button config. | `{ "show": true }` |
| skip       | object  | Yes      | No       | { show: boolean }    | Skip button config. | `{ "show": false }` |
| previous   | object  | Yes      | No       | { show: boolean }    | Previous button config. | `{ "show": true }` |
| home       | object  | Yes      | No       | { show: boolean, timelineItemId: int|null } | Home button config. | `{ "show": true, "timelineItemId": 1 }` |
| next       | object  | Yes      | No       | { show: boolean }    | Next button config. | `{ "show": true }` |
| mute       | object  | Yes      | No       | { show: boolean }    | Mute button config. | `{ "show": false }` |
| fullscreen | object  | Yes      | No       | { show: boolean }    | Fullscreen button config. | `{ "show": true }` |

**Example:**
```json
{
  "show": true,
  "play": { "show": true },
  "skip": { "show": false },
  "previous": { "show": true },
  "home": { "show": true, "timelineItemId": 1 },
  "next": { "show": true },
  "mute": { "show": false },
  "fullscreen": { "show": true }
}
```

---

## 5. snakUrls Object

| Field         | Type | Required | Nullable | Allowed Values/Format | Description | Example |
|---------------|------|----------|----------|----------------------|-------------|---------|
| staticContent | url  | Yes      | Yes      | -                    | URL for static content. | "https://cdn.example.com/static/" |
| font          | url  | Yes      | Yes      | -                    | URL for fonts. | null |
| api           | url  | Yes      | Yes      | -                    | URL for API calls. | "https://api.example.com/" |

**Example:**
```json
{
  "staticContent": "https://cdn.example.com/static/",
  "font": null,
  "api": "https://api.example.com/"
}
```

---

## 6. startBehaviour Format

| Value     | Description |
|-----------|-------------|
| pause     | Player pauses at the start of the timeline item. |
| timer     | Player starts a timer for user input. |
| continue  | Player continues automatically. |
| jump      | Player jumps to another timeline item. |

**Example:**
```json
"startBehaviour": "timer"
```

---

## 7. endBehaviour Format

| Value     | Description |
|-----------|-------------|
| pause     | Player pauses at the end of the timeline item. |
| continue  | Player continues automatically. |
| loop      | Player loops the timeline item. |

**Example:**
```json
"endBehaviour": "loop"
```

---

## 8. timeoutMessage Object

| Field | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|---------|----------|----------|----------------------|-------------|---------|
| show  | boolean | Yes      | No       | true/false           | Show the timeout message. | true |
| text  | string  | Yes      | No       | -                    | Text to display. | "Time's up!" |

**Example:**
```json
{
  "show": true,
  "text": "Time's up!"
}
```

---

## 9. imageMedia Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| id    | uuid   | Yes      | Yes      | -                    | ID of the image media. | null |
| type  | string | Yes      | Yes      | 'image_media'         | Media type. | "image_media" |
| url   | url    | Yes      | No       | -                    | URL of the image. | "https://cdn.example.com/img.png" |

**Example:**
```json
{
  "id": null,
  "type": "image_media",
  "url": "https://cdn.example.com/img.png"
}
```

---

## 10. videoMedia Object

| Field            | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|------------------|---------|----------|----------|----------------------|-------------|---------|
| id               | uuid    | Yes      | No       | -                    | ID of the video media. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |
| type             | string  | Yes      | No       | 'video_media'        | Media type. | "video_media" |
| width            | integer | Yes      | No       | -                    | Pixel width. | 1920 |
| height           | integer | Yes      | No       | -                    | Pixel height. | 1080 |
| url              | url     | Yes      | No       | -                    | URL of the video. | "https://cdn.example.com/video.mp4" |
| previewUrl       | url     | Yes      | No       | -                    | URL of the preview image. | "https://cdn.example.com/preview.jpg" |
| previewFrameCount| integer | Yes      | No       | -                    | Number of preview frames. | 10 |
| previewFrameUrl  | url     | Yes      | No       | -                    | URL for preview frames. | "https://cdn.example.com/frame.jpg" |

**Example:**
```json
{
  "id": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f",
  "type": "video_media",
  "width": 1920,
  "height": 1080,
  "url": "https://cdn.example.com/video.mp4",
  "previewUrl": "https://cdn.example.com/preview.jpg",
  "previewFrameCount": 10,
  "previewFrameUrl": "https://cdn.example.com/frame.jpg"
}
```

---

## 11. soundMedia Object

| Field       | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------------|--------|----------|----------|----------------------|-------------|---------|
| id          | uuid   | Yes      | No       | -                    | ID of the sound media. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |
| type        | string | Yes      | No       | 'sound_media'        | Media type. | "sound_media" |
| url         | url    | Yes      | No       | -                    | URL of the sound. | "https://cdn.example.com/sound.mp3" |
| waveformUrl | url    | Yes      | No       | -                    | URL of the waveform image. | "https://cdn.example.com/waveform.png" |

**Example:**
```json
{
  "id": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f",
  "type": "sound_media",
  "url": "https://cdn.example.com/sound.mp3",
  "waveformUrl": "https://cdn.example.com/waveform.png"
}
```

---

## 12. background Object

| Field   | Type         | Required | Nullable | Allowed Values/Format | Description | Example |
|---------|--------------|----------|----------|----------------------|-------------|---------|
| color   | color        | Yes      | Yes      | 8-digit hex          | Background color. | "#FFBBCC00" |
| image   | imageMedia   | Yes      | Yes      | -                    | Image for background. | null |
| video   | videoMedia   | No       | Yes      | (deprecated)         | Video for background. | null |
| x       | position     | Yes      | Yes      | percent/unit/auto    | X position. | "50%" |
| y       | position     | Yes      | Yes      | percent/unit/auto    | Y position. | "auto" |
| width   | size         | Yes      | Yes      | -                    | Width. | "100%" |
| height  | size         | Yes      | Yes      | -                    | Height. | "100%" |
| repeat  | boolean      | Yes      | Yes      | true/false           | Repeat background image. | true |

**Example:**
```json
{
  "color": "#FFBBCC00",
  "image": null,
  "video": null,
  "x": "50%",
  "y": "auto",
  "width": "100%",
  "height": "100%",
  "repeat": true
}
```

---

## 13. border Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| color | color  | Yes      | Yes      | 8-digit hex          | Border color. | "#FFAABB00" |
| style | string | Yes      | Yes      | none, hidden, dotted, dashed, solid, double, groove, ridge, inset, outset | Border style. | "solid" |
| width | number | Yes      | Yes      | -                    | Border width in pixels. | 2 |
| radius| number | Yes      | Yes      | -                    | Border radius. | 5 |

**Example:**
```json
{
  "color": "#FFAABB00",
  "style": "solid",
  "width": 2,
  "radius": 5
}
```

---

## 14. font Object

| Field         | Type        | Required | Nullable | Allowed Values/Format | Description | Example |
|---------------|------------|----------|----------|----------------------|-------------|---------|
| color         | color      | Yes      | Yes      | 8-digit hex          | Font color. | "#FFAABB00" |
| family        | string     | Yes      | Yes      | -                    | Font family. | "Arial" |
| size          | number     | Yes      | Yes      | -                    | Font size. | 16 |
| weight        | fontWeight | Yes      | Yes      | 'bold' or integer    | Font weight. | "bold" |
| style         | fontStyle  | Yes      | Yes      | normal, italic       | Font style. | "italic" |
| textDecoration| string     | Yes      | Yes      | overline, line, underline, underline overline, none | Text decoration. | "underline" |

**Example:**
```json
{
  "color": "#FFAABB00",
  "family": "Arial",
  "size": 16,
  "weight": "bold",
  "style": "italic",
  "textDecoration": "underline"
}
```

---

## 15. action Object

| Field           | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|-----------------|---------|----------|----------|----------------------|-------------|---------|
| name            | string  | Yes      | No       | none, jump, auto, url, continue, back_to_menu, show_modal, booking | Action name. | "jump" |
| marker          | object  | Yes      | Yes      | See below            | Marker details. | null |
| url             | string  | Yes      | Yes      | -                    | URL for 'url' action. | "https://example.com" |
| openInNewTab    | boolean | Yes      | No       | true/false           | Open URL in new tab. | true |
| modalLayer      | integer | Yes      | Yes      | -                    | Layer index for modal. | 2 |

**Example:**
```json
{
  "name": "jump",
  "marker": {
    "timelineId": 1,
    "time": 5000,
    "trackIndex": 0,
    "linkedTimelineItemId": null
  },
  "url": null,
  "openInNewTab": false,
  "modalLayer": null
}
```

---

## 16. animation Object

| Field         | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|---------------|--------|----------|----------|----------------------|-------------|---------|
| start         | object | Yes      | No       | See below            | Start animation details. | See below |
| loop          | object | Yes      | No       | See below            | Loop animation details. | See below |

**Animation Details:**

| Field           | Type    | Required | Nullable | Allowed Values/Format | Description |
|-----------------|---------|----------|----------|----------------------|-------------|
| name            | string  | Yes      | No       | none, spin_linear, spin, 3d_spin_y, 3d_spin_x, bounce, heartbeat, sway, 3d_sway, breathe, jiggle | Animation name. |
| duration        | integer | Yes      | No       | -                    | Duration. |
| iterationCount* | integer | Yes      | No       | -                    | (start only) Number of times to play. |
| direction       | string  | Yes      | No       | normal, reverse      | Animation direction. |

**Example:**
```json
{
  "start": {
    "name": "bounce",
    "duration": 1000,
    "iterationCount": 2,
    "direction": "normal"
  },
  "loop": {
    "name": "spin",
    "duration": 2000,
    "direction": "reverse"
  }
}
```

---

## 17. graphNodeElement Object

| Field           | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|-----------------|---------|----------|----------|----------------------|-------------|---------|
| id              | uuid    | Yes      | No       | -                    | ID of the graph node element. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |
| type            | string  | Yes      | No       | 'graph_node'         | Element type. | "graph_node" |
| position        | object  | Yes      | No       | See below            | Position and size. | See below |
| content         | string  | Yes      | No       | -                    | Text content. | "Node A" |
| font            | font    | Yes      | No       | -                    | Font configuration. | See [font Object](#font-object) |
| border          | border  | Yes      | No       | -                    | Border configuration. | See [border Object](#border-object) |
| background      | background | Yes      | No       | -                    | Background configuration. | See [background Object](#background-object) |
| action          | action  | Yes      | No       | -                    | Action configuration. | See [action Object](#action-object) |
| animation       | animation | Yes      | No       | -                    | Animation configuration. | See [animation Object](#animation-object) |

**Position and Size:**

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| x     | number | Yes      | No       | -                    | X position. | 100 |
| y     | number | Yes      | No       | -                    | Y position. | 100 |
| width | number | Yes      | No       | -                    | Width. | 200 |
| height| number | Yes      | No       | -                    | Height. | 100 |

**Example:**
```json
{
  "id": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f",
  "type": "graph_node",
  "position": { "x": 100, "y": 100, "width": 200, "height": 100 },
  "content": "Node A",
  "font": { "color": "#FF0000", "family": "Arial", "size": 16, "weight": "bold", "style": "italic", "textDecoration": "underline" },
  "border": { "color": "#FFAABB00", "style": "solid", "width": 2, "radius": 5 },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "action": { "name": "jump", "marker": { "timelineId": 1, "time": 5000, "trackIndex": 0, "linkedTimelineItemId": null }, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 1000, "iterationCount": 2, "direction": "normal" }, "loop": { "name": "spin", "duration": 2000, "direction": "reverse" } }
}
```

---

## 18. ratingItem Object

| Field           | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|-----------------|---------|----------|----------|----------------------|-------------|---------|
| id              | uuid    | Yes      | No       | -                    | ID of the rating item. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |
| type            | string  | Yes      | No       | 'rating'             | Item type. | "rating" |
| position        | object  | Yes      | No       | See below            | Position and size. | See below |
| content         | string  | Yes      | No       | -                    | Text content. | "Rate Us" |
| font            | font    | Yes      | No       | -                    | Font configuration. | See [font Object](#font-object) |
| border          | border  | Yes      | No       | -                    | Border configuration. | See [border Object](#border-object) |
| background      | background | Yes      | No       | -                    | Background configuration. | See [background Object](#background-object) |
| action          | action  | Yes      | No       | -                    | Action configuration. | See [action Object](#action-object) |
| animation       | animation | Yes      | No       | -                    | Animation configuration. | See [animation Object](#animation-object) |

**Position and Size:**

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| x     | number | Yes      | No       | -                    | X position. | 100 |
| y     | number | Yes      | No       | -                    | Y position. | 100 |
| width | number | Yes      | No       | -                    | Width. | 200 |
| height| number | Yes      | No       | -                    | Height. | 100 |

**Example:**
```json
{
  "id": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f",
  "type": "rating",
  "position": { "x": 100, "y": 100, "width": 200, "height": 100 },
  "content": "Rate Us",
  "font": { "color": "#FF0000", "family": "Arial", "size": 16, "weight": "bold", "style": "italic", "textDecoration": "underline" },
  "border": { "color": "#FFAABB00", "style": "solid", "width": 2, "radius": 5 },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "action": { "name": "jump", "marker": { "timelineId": 1, "time": 5000, "trackIndex": 0, "linkedTimelineItemId": null }, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 1000, "iterationCount": 2, "direction": "normal" }, "loop": { "name": "spin", "duration": 2000, "direction": "reverse" } }
}
```

---

## 19. rankingItem Object

| Field           | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|-----------------|---------|----------|----------|----------------------|-------------|---------|
| id              | uuid    | Yes      | No       | -                    | ID of the ranking item. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |
| type            | string  | Yes      | No       | 'ranking'            | Item type. | "ranking" |
| position        | object  | Yes      | No       | See below            | Position and size. | See below |
| content         | string  | Yes      | No       | -                    | Text content. | "Ranking" |
| font            | font    | Yes      | No       | -                    | Font configuration. | See [font Object](#font-object) |
| border          | border  | Yes      | No       | -                    | Border configuration. | See [border Object](#border-object) |
| background      | background | Yes      | No       | -                    | Background configuration. | See [background Object](#background-object) |
| action          | action  | Yes      | No       | -                    | Action configuration. | See [action Object](#action-object) |
| animation       | animation | Yes      | No       | -                    | Animation configuration. | See [animation Object](#animation-object) |

**Position and Size:**

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| x     | number | Yes      | No       | -                    | X position. | 100 |
| y     | number | Yes      | No       | -                    | Y position. | 100 |
| width | number | Yes      | No       | -                    | Width. | 200 |
| height| number | Yes      | No       | -                    | Height. | 100 |

**Example:**
```json
{
  "id": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f",
  "type": "ranking",
  "position": { "x": 100, "y": 100, "width": 200, "height": 100 },
  "content": "Ranking",
  "font": { "color": "#FF0000", "family": "Arial", "size": 16, "weight": "bold", "style": "italic", "textDecoration": "underline" },
  "border": { "color": "#FFAABB00", "style": "solid", "width": 2, "radius": 5 },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "action": { "name": "jump", "marker": { "timelineId": 1, "time": 5000, "trackIndex": 0, "linkedTimelineItemId": null }, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 1000, "iterationCount": 2, "direction": "normal" }, "loop": { "name": "spin", "duration": 2000, "direction": "reverse" } }
}
```

---

## 20. tag Object

| Field           | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|-----------------|---------|----------|----------|----------------------|-------------|---------|
| id              | uuid    | Yes      | No       | -                    | ID of the tag. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |
| type            | string  | Yes      | No       | 'tag'                | Item type. | "tag" |
| position        | object  | Yes      | No       | See below            | Position and size. | See below |
| content         | string  | Yes      | No       | -                    | Text content. | "Tag A" |
| font            | font    | Yes      | No       | -                    | Font configuration. | See [font Object](#font-object) |
| border          | border  | Yes      | No       | -                    | Border configuration. | See [border Object](#border-object) |
| background      | background | Yes      | No       | -                    | Background configuration. | See [background Object](#background-object) |
| action          | action  | Yes      | No       | -                    | Action configuration. | See [action Object](#action-object) |
| animation       | animation | Yes      | No       | -                    | Animation configuration. | See [animation Object](#animation-object) |

**Position and Size:**

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| x     | number | Yes      | No       | -                    | X position. | 100 |
| y     | number | Yes      | No       | -                    | Y position. | 100 |
| width | number | Yes      | No       | -                    | Width. | 200 |
| height| number | Yes      | No       | -                    | Height. | 100 |

**Example:**
```json
{
  "id": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f",
  "type": "tag",
  "position": { "x": 100, "y": 100, "width": 200, "height": 100 },
  "content": "Tag A",
  "font": { "color": "#FF0000", "family": "Arial", "size": 16, "weight": "bold", "style": "italic", "textDecoration": "underline" },
  "border": { "color": "#FFAABB00", "style": "solid", "width": 2, "radius": 5 },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "action": { "name": "jump", "marker": { "timelineId": 1, "time": 5000, "trackIndex": 0, "linkedTimelineItemId": null }, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 1000, "iterationCount": 2, "direction": "normal" }, "loop": { "name": "spin", "duration": 2000, "direction": "reverse" } }
}
```

---

## 21. layer Object

| Field           | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|-----------------|---------|----------|----------|----------------------|-------------|---------|
| id              | uuid    | Yes      | No       | -                    | ID of the layer. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |
| type            | string  | Yes      | No       | 'layer'              | Item type. | "layer" |
| position        | object  | Yes      | No       | See below            | Position and size. | See below |
| content         | string  | Yes      | No       | -                    | Text content. | "Layer A" |
| font            | font    | Yes      | No       | -                    | Font configuration. | See [font Object](#font-object) |
| border          | border  | Yes      | No       | -                    | Border configuration. | See [border Object](#border-object) |
| background      | background | Yes      | No       | -                    | Background configuration. | See [background Object](#background-object) |
| action          | action  | Yes      | No       | -                    | Action configuration. | See [action Object](#action-object) |
| animation       | animation | Yes      | No       | -                    | Animation configuration. | See [animation Object](#animation-object) |

**Position and Size:**

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| x     | number | Yes      | No       | -                    | X position. | 100 |
| y     | number | Yes      | No       | -                    | Y position. | 100 |
| width | number | Yes      | No       | -                    | Width. | 200 |
| height| number | Yes      | No       | -                    | Height. | 100 |

**Example:**
```json
{
  "id": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f",
  "type": "layer",
  "position": { "x": 100, "y": 100, "width": 200, "height": 100 },
  "content": "Layer A",
  "font": { "color": "#FF0000", "family": "Arial", "size": 16, "weight": "bold", "style": "italic", "textDecoration": "underline" },
  "border": { "color": "#FFAABB00", "style": "solid", "width": 2, "radius": 5 },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "action": { "name": "jump", "marker": { "timelineId": 1, "time": 5000, "trackIndex": 0, "linkedTimelineItemId": null }, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 1000, "iterationCount": 2, "direction": "normal" }, "loop": { "name": "spin", "duration": 2000, "direction": "reverse" } }
}
```

---

## 22. timeline Object

| Field           | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|-----------------|---------|----------|----------|----------------------|-------------|---------|
| id              | uuid    | Yes      | No       | -                    | ID of the timeline. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |
| type            | string  | Yes      | No       | 'timeline'           | Item type. | "timeline" |
| position        | object  | Yes      | No       | See below            | Position and size. | See below |
| content         | string  | Yes      | No       | -                    | Text content. | "Timeline A" |
| font            | font    | Yes      | No       | -                    | Font configuration. | See [font Object](#font-object) |
| border          | border  | Yes      | No       | -                    | Border configuration. | See [border Object](#border-object) |
| background      | background | Yes      | No       | -                    | Background configuration. | See [background Object](#background-object) |
| action          | action  | Yes      | No       | -                    | Action configuration. | See [action Object](#action-object) |
| animation       | animation | Yes      | No       | -                    | Animation configuration. | See [animation Object](#animation-object) |

**Position and Size:**

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| x     | number | Yes      | No       | -                    | X position. | 100 |
| y     | number | Yes      | No       | -                    | Y position. | 100 |
| width | number | Yes      | No       | -                    | Width. | 200 |
| height| number | Yes      | No       | -                    | Height. | 100 |

**Example:**
```json
{
  "id": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f",
  "type": "timeline",
  "position": { "x": 100, "y": 100, "width": 200, "height": 100 },
  "content": "Timeline A",
  "font": { "color": "#FF0000", "family": "Arial", "size": 16, "weight": "bold", "style": "italic", "textDecoration": "underline" },
  "border": { "color": "#FFAABB00", "style": "solid", "width": 2, "radius": 5 },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "action": { "name": "jump", "marker": { "timelineId": 1, "time": 5000, "trackIndex": 0, "linkedTimelineItemId": null }, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 1000, "iterationCount": 2, "direction": "normal" }, "loop": { "name": "spin", "duration": 2000, "direction": "reverse" } }
}
```

---

## 23. timelineItem Object

| Field           | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|-----------------|---------|----------|----------|----------------------|-------------|---------|
| id              | uuid    | Yes      | No       | -                    | ID of the timeline item. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |
| type            | string  | Yes      | No       | 'timeline_item'      | Item type. | "timeline_item" |
| position        | object  | Yes      | No       | See below            | Position and size. | See below |
| content         | string  | Yes      | No       | -                    | Text content. | "Item A" |
| font            | font    | Yes      | No       | -                    | Font configuration. | See [font Object](#font-object) |
| border          | border  | Yes      | No       | -                    | Border configuration. | See [border Object](#border-object) |
| background      | background | Yes      | No       | -                    | Background configuration. | See [background Object](#background-object) |
| action          | action  | Yes      | No       | -                    | Action configuration. | See [action Object](#action-object) |
| animation       | animation | Yes      | No       | -                    | Animation configuration. | See [animation Object](#animation-object) |

**Position and Size:**

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| x     | number | Yes      | No       | -                    | X position. | 100 |
| y     | number | Yes      | No       | -                    | Y position. | 100 |
| width | number | Yes      | No       | -                    | Width. | 200 |
| height| number | Yes      | No       | -                    | Height. | 100 |

**Example:**
```json
{
  "id": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f",
  "type": "timeline_item",
  "position": { "x": 100, "y": 100, "width": 200, "height": 100 },
  "content": "Item A",
  "font": { "color": "#FF0000", "family": "Arial", "size": 16, "weight": "bold", "style": "italic", "textDecoration": "underline" },
  "border": { "color": "#FFAABB00", "style": "solid", "width": 2, "radius": 5 },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "action": { "name": "jump", "marker": { "timelineId": 1, "time": 5000, "trackIndex": 0, "linkedTimelineItemId": null }, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 1000, "iterationCount": 2, "direction": "normal" }, "loop": { "name": "spin", "duration": 2000, "direction": "reverse" } }
}
```

---

## 24. node Object

| Field           | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|-----------------|---------|----------|----------|----------------------|-------------|---------|
| id              | uuid    | Yes      | No       | -                    | ID of the node. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |
| type            | string  | Yes      | No       | 'node'               | Item type. | "node" |
| position        | object  | Yes      | No       | See below            | Position and size. | See below |
| content         | string  | Yes      | No       | -                    | Text content. | "Node A" |
| font            | font    | Yes      | No       | -                    | Font configuration. | See [font Object](#font-object) |
| border          | border  | Yes      | No       | -                    | Border configuration. | See [border Object](#border-object) |
| background      | background | Yes      | No       | -                    | Background configuration. | See [background Object](#background-object) |
| action          | action  | Yes      | No       | -                    | Action configuration. | See [action Object](#action-object) |
| animation       | animation | Yes      | No       | -                    | Animation configuration. | See [animation Object](#animation-object) |

**Position and Size:**

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| x     | number | Yes      | No       | -                    | X position. | 100 |
| y     | number | Yes      | No       | -                    | Y position. | 100 |
| width | number | Yes      | No       | -                    | Width. | 200 |
| height| number | Yes      | No       | -                    | Height. | 100 |

**Example:**
```json
{
  "id": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f",
  "type": "node",
  "position": { "x": 100, "y": 100, "width": 200, "height": 100 },
  "content": "Node A",
  "font": { "color": "#FF0000", "family": "Arial", "size": 16, "weight": "bold", "style": "italic", "textDecoration": "underline" },
  "border": { "color": "#FFAABB00", "style": "solid", "width": 2, "radius": 5 },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "action": { "name": "jump", "marker": { "timelineId": 1, "time": 5000, "trackIndex": 0, "linkedTimelineItemId": null }, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 1000, "iterationCount": 2, "direction": "normal" }, "loop": { "name": "spin", "duration": 2000, "direction": "reverse" } }
}
```

---

## 25. theme Object

| Field           | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|-----------------|---------|----------|----------|----------------------|-------------|---------|
| id              | uuid    | Yes      | No       | -                    | ID of the theme. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |
| type            | string  | Yes      | No       | 'theme'              | Item type. | "theme" |
| position        | object  | Yes      | No       | See below            | Position and size. | See below |
| content         | string  | Yes      | No       | -                    | Text content. | "Theme A" |
| font            | font    | Yes      | No       | -                    | Font configuration. | See [font Object](#font-object) |
| border          | border  | Yes      | No       | -                    | Border configuration. | See [border Object](#border-object) |
| background      | background | Yes      | No       | -                    | Background configuration. | See [background Object](#background-object) |
| action          | action  | Yes      | No       | -                    | Action configuration. | See [action Object](#action-object) |
| animation       | animation | Yes      | No       | -                    | Animation configuration. | See [animation Object](#animation-object) |

**Position and Size:**

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| x     | number | Yes      | No       | -                    | X position. | 100 |
| y     | number | Yes      | No       | -                    | Y position. | 100 |
| width | number | Yes      | No       | -                    | Width. | 200 |
| height| number | Yes      | No       | -                    | Height. | 100 |

**Example:**
```json
{
  "id": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f",
  "type": "theme",
  "position": { "x": 100, "y": 100, "width": 200, "height": 100 },
  "content": "Theme A",
  "font": { "color": "#FF0000", "family": "Arial", "size": 16, "weight": "bold", "style": "italic", "textDecoration": "underline" },
  "border": { "color": "#FFAABB00", "style": "solid", "width": 2, "radius": 5 },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "action": { "name": "jump", "marker": { "timelineId": 1, "time": 5000, "trackIndex": 0, "linkedTimelineItemId": null }, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 1000, "iterationCount": 2, "direction": "normal" }, "loop": { "name": "spin", "duration": 2000, "direction": "reverse" } }
}
```

---

## 26. color Object

| Field           | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|-----------------|---------|----------|----------|----------------------|-------------|---------|
| id              | uuid    | Yes      | No       | -                    | ID of the color. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |
| type            | string  | Yes      | No       | 'color'              | Item type. | "color" |
| position        | object  | Yes      | No       | See below            | Position and size. | See below |
| content         | string  | Yes      | No       | -                    | Text content. | "Color A" |
| font            | font    | Yes      | No       | -                    | Font configuration. | See [font Object](#font-object) |
| border          | border  | Yes      | No       | -                    | Border configuration. | See [border Object](#border-object) |
| background      | background | Yes      | No       | -                    | Background configuration. | See [background Object](#background-object) |
| action          | action  | Yes      | No       | -                    | Action configuration. | See [action Object](#action-object) |
| animation       | animation | Yes      | No       | -                    | Animation configuration. | See [animation Object](#animation-object) |

**Position and Size:**

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| x     | number | Yes      | No       | -                    | X position. | 100 |
| y     | number | Yes      | No       | -                    | Y position. | 100 |
| width | number | Yes      | No       | -                    | Width. | 200 |
| height| number | Yes      | No       | -                    | Height. | 100 |

**Example:**
```json
{
  "id": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f",
  "type": "color",
  "position": { "x": 100, "y": 100, "width": 200, "height": 100 },
  "content": "Color A",
  "font": { "color": "#FF0000", "family": "Arial", "size": 16, "weight": "bold", "style": "italic", "textDecoration": "underline" },
  "border": { "color": "#FFAABB00", "style": "solid", "width": 2, "radius": 5 },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "action": { "name": "jump", "marker": { "timelineId": 1, "time": 5000, "trackIndex": 0, "linkedTimelineItemId": null }, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 1000, "iterationCount": 2, "direction": "normal" }, "loop": { "name": "spin", "duration": 2000, "direction": "reverse" } }
}
```

---

## 27. position Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| x     | number | Yes      | No       | -                    | X position. | 100 |
| y     | number | Yes      | No       | -                    | Y position. | 100 |

**Example:**
```json
{ "x": 100, "y": 100 }
```

---

## 28. size Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| width | number | Yes      | No       | -                    | Width. | 100 |
| height| number | Yes      | No       | -                    | Height. | 100 |

**Example:**
```json
{ "width": 100, "height": 100 }
```

---

## 29. fontWeight Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | string | Yes      | No       | 'bold' or integer    | Font weight. | "bold" |

**Example:**
```json
{ "value": "bold" }
```

---

## 30. fontStyle Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | string | Yes      | No       | normal, italic       | Font style. | "italic" |

**Example:**
```json
{ "value": "italic" }
```

---

## 31. textDecoration Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | string | Yes      | No       | overline, line, underline, underline overline, none | Text decoration. | "underline" |

**Example:**
```json
{ "value": "underline" }
```

---

## 32. aspectRatio Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | string | Yes      | No       | String, e.g. '6:9'   | The aspect ratio of the Snak. | "16:9" |

**Example:**
```json
{ "value": "16:9" }
```

---

## 33. url Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | string | Yes      | No       | -                    | URL. | "https://example.com" |

**Example:**
```json
{ "value": "https://example.com" }
```

---

## 34. boolean Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | boolean | Yes      | No       | true/false           | Boolean value. | true |

**Example:**
```json
{ "value": true }
```

---

## 35. integer Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | integer | Yes      | No       | -                    | Integer value. | 100 |

**Example:**
```json
{ "value": 100 }
```

---

## 36. uuid Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | uuid   | Yes      | No       | -                    | UUID. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |

**Example:**
```json
{ "value": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" }
```

---

## 37. string Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | string | Yes      | No       | -                    | String value. | "Hello" |

**Example:**
```json
{ "value": "Hello" }
```

---

## 38. array Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | array  | Yes      | No       | -                    | Array of values. | ["a", "b"] |

**Example:**
```json
{ "value": ["a", "b"] }
```

---

## 39. object Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | object | Yes      | No       | -                    | Object value. | { "a": 1 } |

**Example:**
```json
{ "value": { "a": 1 } }
```

---

## 40. null Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | null   | Yes      | No       | -                    | Null value. | null |

**Example:**
```json
{ "value": null }
```

---

## 41. color Object

| Field           | Type    | Required | Nullable | Allowed Values/Format | Description | Example |
|-----------------|---------|----------|----------|----------------------|-------------|---------|
| id              | uuid    | Yes      | No       | -                    | ID of the color. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |
| type            | string  | Yes      | No       | 'color'              | Item type. | "color" |
| position        | object  | Yes      | No       | See below            | Position and size. | See below |
| content         | string  | Yes      | No       | -                    | Text content. | "Color A" |
| font            | font    | Yes      | No       | -                    | Font configuration. | See [font Object](#font-object) |
| border          | border  | Yes      | No       | -                    | Border configuration. | See [border Object](#border-object) |
| background      | background | Yes      | No       | -                    | Background configuration. | See [background Object](#background-object) |
| action          | action  | Yes      | No       | -                    | Action configuration. | See [action Object](#action-object) |
| animation       | animation | Yes      | No       | -                    | Animation configuration. | See [animation Object](#animation-object) |

**Position and Size:**

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| x     | number | Yes      | No       | -                    | X position. | 100 |
| y     | number | Yes      | No       | -                    | Y position. | 100 |
| width | number | Yes      | No       | -                    | Width. | 200 |
| height| number | Yes      | No       | -                    | Height. | 100 |

**Example:**
```json
{
  "id": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f",
  "type": "color",
  "position": { "x": 100, "y": 100, "width": 200, "height": 100 },
  "content": "Color A",
  "font": { "color": "#FF0000", "family": "Arial", "size": 16, "weight": "bold", "style": "italic", "textDecoration": "underline" },
  "border": { "color": "#FFAABB00", "style": "solid", "width": 2, "radius": 5 },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "action": { "name": "jump", "marker": { "timelineId": 1, "time": 5000, "trackIndex": 0, "linkedTimelineItemId": null }, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 1000, "iterationCount": 2, "direction": "normal" }, "loop": { "name": "spin", "duration": 2000, "direction": "reverse" } }
}
```

---

## 42. position Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| x     | number | Yes      | No       | -                    | X position. | 100 |
| y     | number | Yes      | No       | -                    | Y position. | 100 |

**Example:**
```json
{ "x": 100, "y": 100 }
```

---

## 43. size Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| width | number | Yes      | No       | -                    | Width. | 100 |
| height| number | Yes      | No       | -                    | Height. | 100 |

**Example:**
```json
{ "width": 100, "height": 100 }
```

---

## 44. fontWeight Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | string | Yes      | No       | 'bold' or integer    | Font weight. | "bold" |

**Example:**
```json
{ "value": "bold" }
```

---

## 45. fontStyle Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | string | Yes      | No       | normal, italic       | Font style. | "italic" |

**Example:**
```json
{ "value": "italic" }
```

---

## 46. textDecoration Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | string | Yes      | No       | overline, line, underline, underline overline, none | Text decoration. | "underline" |

**Example:**
```json
{ "value": "underline" }
```

---

## 47. aspectRatio Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | string | Yes      | No       | String, e.g. '6:9'   | The aspect ratio of the Snak. | "16:9" |

**Example:**
```json
{ "value": "16:9" }
```

---

## 48. url Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | string | Yes      | No       | -                    | URL. | "https://example.com" |

**Example:**
```json
{ "value": "https://example.com" }
```

---

## 49. boolean Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | boolean | Yes      | No       | true/false           | Boolean value. | true |

**Example:**
```json
{ "value": true }
```

---

## 50. integer Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | integer | Yes      | No       | -                    | Integer value. | 100 |

**Example:**
```json
{ "value": 100 }
```

---

## 51. uuid Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | uuid   | Yes      | No       | -                    | UUID. | "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" |

**Example:**
```json
{ "value": "b3e1f2c0-1234-4a5b-8c2d-1a2b3c4d5e6f" }
```

---

## 52. string Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | string | Yes      | No       | -                    | String value. | "Hello" |

**Example:**
```json
{ "value": "Hello" }
```

---

## 53. array Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | array  | Yes      | No       | -                    | Array of values. | ["a", "b"] |

**Example:**
```json
{ "value": ["a", "b"] }
```

---

## 54. object Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | object | Yes      | No       | -                    | Object value. | { "a": 1 } |

**Example:**
```json
{ "value": { "a": 1 } }
```

---

## 55. null Object

| Field | Type   | Required | Nullable | Allowed Values/Format | Description | Example |
|-------|--------|----------|----------|----------------------|-------------|---------|
| value | null   | Yes      | No       | -                    | Null value. | null |

**Example:**
```json
{ "value": null }
``` 

---

# Timeline Item Subtypes

## 23.1 Generic Cue Timeline Item (generic_tli)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the timeline item. |
| name | string | Yes | No | - | The name of the timeline item. |
| label | string | Yes | Yes | - | The label of the timeline item. |
| type | timelineItemType | Yes | No | 'generic_tli' | The type of the timeline item. |
| themePrefix | string | Yes | No | - | The prefix to use when looking up theme values. |
| startTime | integer | Yes | No | - | The start time this timeline item appears on the timeline. |
| endTime | integer | Yes | No | - | The time the timeline item ends on the timeline. |
| startBehaviour | startBehaviour | Yes | No | pause, timer, continue, jump | What the player does when the start of the timeline item is reached. |
| endBehaviour | endBehaviour | Yes | No | pause, continue, loop | What the player does when the end of the timeline item is reached. |
| answerTime | integer | Yes | No | - | The amount of milliseconds the user has to answer the cue if 'timer' was selected for start behaviour. |
| timeoutMessage | timeoutMessage | Yes | No | - | Timeout message configuration. |
| background | background | Yes | No | - | Background to use for the timeline item. |
| showOverlay | boolean | Yes | Yes | - | True to show the overlay. |
| tags | tags | Yes | No | - | Tags associated with the timeline item. |
| layers | array(layer) | Yes | No | - | All layers available for the timeline item. |
| nodes | array(node) | Yes | No | - | All nodes within the timeline item. |

**Example:**
```json
{
  "id": 1,
  "name": "Intro",
  "label": "Introduction",
  "type": "generic_tli",
  "themePrefix": "default",
  "startTime": 0,
  "endTime": 10000,
  "startBehaviour": "pause",
  "endBehaviour": "continue",
  "answerTime": 5000,
  "timeoutMessage": { "show": true, "text": "Time's up!" },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "showOverlay": true,
  "tags": ["intro"],
  "layers": [],
  "nodes": []
}
```

## 23.2 Menu Cue Timeline Item (menu_tli)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the timeline item. |
| name | string | Yes | No | - | The name of the timeline item. |
| label | string | Yes | Yes | - | The label of the timeline item. |
| type | timelineItemType | Yes | No | 'menu_tli' | The type of the timeline item. |
| themePrefix | string | Yes | No | - | The prefix to use when looking up theme values. |
| startTime | integer | Yes | No | - | The start time this timeline item appears on the timeline. |
| endTime | integer | Yes | No | - | The time the timeline item ends on the timeline. |
| startBehaviour | startBehaviour | Yes | No | pause, timer, continue, jump | What the player does when the start of the timeline item is reached. |
| endBehaviour | endBehaviour | Yes | No | pause, continue, loop | What the player does when the end of the timeline item is reached. |
| answerTime | integer | Yes | No | - | The amount of milliseconds the user has to answer the cue if 'timer' was selected for start behaviour. |
| timeoutMessage | timeoutMessage | Yes | No | - | Timeout message configuration. |
| background | background | Yes | No | - | Background to use for the timeline item. |
| showOverlay | boolean | Yes | Yes | - | True to show the overlay. |
| tags | tags | Yes | No | - | Tags associated with the timeline item. |
| showWheelOfFortune | boolean | Yes | No | - | True to display the menu as a wheel of fortune. |
| layers | array(layer) | Yes | No | - | All layers available for the timeline item. |
| nodes | array(node) | Yes | No | - | All nodes within the timeline item. |

**Example:**
```json
{
  "id": 2,
  "name": "Menu",
  "label": "Choose an option",
  "type": "menu_tli",
  "themePrefix": "default",
  "startTime": 10000,
  "endTime": 20000,
  "startBehaviour": "pause",
  "endBehaviour": "continue",
  "answerTime": 10000,
  "timeoutMessage": { "show": true, "text": "Please choose!" },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "showOverlay": true,
  "tags": ["menu"],
  "showWheelOfFortune": false,
  "layers": [],
  "nodes": []
}
```

## 23.3 Yes/No Cue Timeline Item (yesno_tli)
| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the timeline item. |
| name | string | Yes | No | - | The name of the timeline item. |
| label | string | Yes | Yes | - | The label of the timeline item. |
| type | timelineItemType | Yes | No | 'yesno_tli' | The type of the timeline item. |
| themePrefix | string | Yes | No | - | The prefix to use when looking up theme values. |
| startTime | integer | Yes | No | - | The start time this timeline item appears on the timeline. |
| endTime | integer | Yes | No | - | The time the timeline item ends on the timeline. |
| startBehaviour | startBehaviour | Yes | No | pause, timer, continue, jump | What the player does when the start of the timeline item is reached. |
| endBehaviour | endBehaviour | Yes | No | pause, continue, loop | What the player does when the end of the timeline item is reached. |
| answerTime | integer | Yes | No | - | The amount of milliseconds the user has to answer the cue if 'timer' was selected for start behaviour. |
| timeoutMessage | timeoutMessage | Yes | No | - | Timeout message configuration. |
| background | background | Yes | No | - | Background to use for the timeline item. |
| showOverlay | boolean | Yes | Yes | - | True to show the overlay. |
| tags | tags | Yes | No | - | Tags associated with the timeline item. |
| feedbackType | string | Yes | No | quiz, poll | The feedback type to display. |
| showFeedback | boolean | Yes | No | - | True to show feedback after an answer. |
| showBreadcrumbs | boolean | Yes | No | - | True to show breadcrumbs on the feedback. |
| showPercentages | boolean | Yes | No | - | True to show percentages on the feedback. |
| layers | array(layer) | Yes | No | - | All layers available for the timeline item. |
| nodes | array(node) | Yes | No | - | All nodes within the timeline item. |

**Example:**
```json
{
  "id": 3,
  "name": "Yes/No Question",
  "label": "Do you agree?",
  "type": "yesno_tli",
  "themePrefix": "default",
  "startTime": 20000,
  "endTime": 30000,
  "startBehaviour": "timer",
  "endBehaviour": "pause",
  "answerTime": 8000,
  "timeoutMessage": { "show": true, "text": "Please answer!" },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "showOverlay": false,
  "tags": ["yesno"],
  "feedbackType": "quiz",
  "showFeedback": true,
  "showBreadcrumbs": true,
  "showPercentages": false,
  "layers": [],
  "nodes": []
}
```

## 23.4 Multiple Choice Cue Timeline Item (multiple_choice_tli)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the timeline item. |
| name | string | Yes | No | - | The name of the timeline item. |
| label | string | Yes | Yes | - | The label of the timeline item. |
| type | timelineItemType | Yes | No | 'multiple_choice_tli' | The type of the timeline item. |
| themePrefix | string | Yes | No | - | The prefix to use when looking up theme values. |
| startTime | integer | Yes | No | - | The start time this timeline item appears on the timeline. |
| endTime | integer | Yes | No | - | The time the timeline item ends on the timeline. |
| startBehaviour | startBehaviour | Yes | No | pause, timer, continue, jump | What the player does when the start of the timeline item is reached. |
| endBehaviour | endBehaviour | Yes | No | pause, continue, loop | What the player does when the end of the timeline item is reached. |
| answerTime | integer | Yes | No | - | The amount of milliseconds the user has to answer the cue if 'timer' was selected for start behaviour. |
| timeoutMessage | timeoutMessage | Yes | No | - | Timeout message configuration. |
| background | background | Yes | No | - | Background to use for the timeline item. |
| showOverlay | boolean | Yes | Yes | - | True to show the overlay. |
| tags | tags | Yes | No | - | Tags associated with the timeline item. |
| feedbackType | string | Yes | No | quiz, poll | The feedback type to display. |
| showFeedback | boolean | Yes | No | - | True to show feedback after an answer. |
| showBreadcrumbs | boolean | Yes | No | - | True to show breadcrumbs on the feedback. |
| showPercentages | boolean | Yes | No | - | True to show percentages on the feedback. |
| layers | array(layer) | Yes | No | - | All layers available for the timeline item. |
| nodes | array(node) | Yes | No | - | All nodes within the timeline item. |

**Example:**
```json
{
  "id": 4,
  "name": "Multiple Choice Question",
  "label": "Select the correct answer:",
  "type": "multiple_choice_tli",
  "themePrefix": "default",
  "startTime": 30000,
  "endTime": 40000,
  "startBehaviour": "timer",
  "endBehaviour": "pause",
  "answerTime": 10000,
  "timeoutMessage": { "show": true, "text": "Please answer!" },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "showOverlay": true,
  "tags": ["mcq"],
  "feedbackType": "quiz",
  "showFeedback": true,
  "showBreadcrumbs": false,
  "showPercentages": true,
  "layers": [],
  "nodes": []
}
```

## 23.5 Multiple Select Cue Timeline Item (multiple_select_tli)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the timeline item. |
| name | string | Yes | No | - | The name of the timeline item. |
| label | string | Yes | Yes | - | The label of the timeline item. |
| type | timelineItemType | Yes | No | 'multiple_select_tli' | The type of the timeline item. |
| themePrefix | string | Yes | No | - | The prefix to use when looking up theme values. |
| startTime | integer | Yes | No | - | The start time this timeline item appears on the timeline. |
| endTime | integer | Yes | No | - | The time the timeline item ends on the timeline. |
| startBehaviour | startBehaviour | Yes | No | pause, timer, continue, jump | What the player does when the start of the timeline item is reached. |
| endBehaviour | endBehaviour | Yes | No | pause, continue, loop | What the player does when the end of the timeline item is reached. |
| answerTime | integer | Yes | No | - | The amount of milliseconds the user has to answer the cue if 'timer' was selected for start behaviour. |
| timeoutMessage | timeoutMessage | Yes | No | - | Timeout message configuration. |
| background | background | Yes | No | - | Background to use for the timeline item. |
| showOverlay | boolean | Yes | Yes | - | True to show the overlay. |
| tags | tags | Yes | No | - | Tags associated with the timeline item. |
| feedbackType | string | Yes | No | quiz, poll | The feedback type to display. |
| showFeedback | boolean | Yes | No | - | True to show feedback after an answer. |
| showBreadcrumbs | boolean | Yes | No | - | True to show breadcrumbs on the feedback. |
| showPercentages | boolean | Yes | No | - | True to show percentages on the feedback. |
| feedbackPollMessage | string | Yes | Yes | - | Message to show for poll feedback. |
| feedbackCorrectMessage | string | Yes | Yes | - | Message to show for correct answers. |
| feedbackIncorrectMessage | string | Yes | Yes | - | Message to show for incorrect answers. |
| maxAnswers | integer | Yes | No | - | Maximum number of answers allowed. |
| minAnswers | integer | Yes | No | - | Minimum number of answers required. |
| showCheckboxes | boolean | Yes | No | - | True to show checkboxes for selection. |
| layers | array(layer) | Yes | No | - | All layers available for the timeline item. |
| nodes | array(node) | Yes | No | - | All nodes within the timeline item. |

**Example:**
```json
{
  "id": 5,
  "name": "Select All That Apply",
  "label": "Choose all correct answers:",
  "type": "multiple_select_tli",
  "themePrefix": "default",
  "startTime": 40000,
  "endTime": 50000,
  "startBehaviour": "timer",
  "endBehaviour": "pause",
  "answerTime": 12000,
  "timeoutMessage": { "show": true, "text": "Please answer!" },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "showOverlay": true,
  "tags": ["msq"],
  "feedbackType": "poll",
  "showFeedback": true,
  "showBreadcrumbs": false,
  "showPercentages": true,
  "feedbackPollMessage": "Most people chose option B.",
  "feedbackCorrectMessage": "Correct!",
  "feedbackIncorrectMessage": "Try again!",
  "maxAnswers": 3,
  "minAnswers": 1,
  "showCheckboxes": true,
  "layers": [],
  "nodes": []
}
```

## 23.6 Audience Select Cue Timeline Item (audience_select_tli)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the timeline item. |
| name | string | Yes | No | - | The name of the timeline item. |
| label | string | Yes | Yes | - | The label of the timeline item. |
| type | timelineItemType | Yes | No | 'audience_select_tli' | The type of the timeline item. |
| themePrefix | string | Yes | No | - | The prefix to use when looking up theme values. |
| startTime | integer | Yes | No | - | The start time this timeline item appears on the timeline. |
| endTime | integer | Yes | No | - | The time the timeline item ends on the timeline. |
| startBehaviour | startBehaviour | Yes | No | pause, timer, continue, jump | What the player does when the start of the timeline item is reached. |
| endBehaviour | endBehaviour | Yes | No | pause, continue, loop | What the player does when the end of the timeline item is reached. |
| answerTime | integer | Yes | No | - | The amount of milliseconds the user has to answer the cue if 'timer' was selected for start behaviour. |
| timeoutMessage | timeoutMessage | Yes | No | - | Timeout message configuration. |
| background | background | Yes | No | - | Background to use for the timeline item. |
| showOverlay | boolean | Yes | Yes | - | True to show the overlay. |
| tags | tags | Yes | No | - | Tags associated with the timeline item. |
| layers | array(layer) | Yes | No | - | All layers available for the timeline item. |
| nodes | array(node) | Yes | No | - | All nodes within the timeline item. |

**Example:**
```json
{
  "id": 6,
  "name": "Audience Select",
  "label": "Select your group:",
  "type": "audience_select_tli",
  "themePrefix": "default",
  "startTime": 50000,
  "endTime": 60000,
  "startBehaviour": "pause",
  "endBehaviour": "continue",
  "answerTime": 15000,
  "timeoutMessage": { "show": true, "text": "Please select!" },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "showOverlay": true,
  "tags": ["audience"],
  "layers": [],
  "nodes": []
}
```

## 23.7 Rating Cue Timeline Item (rating_tli)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the timeline item. |
| name | string | Yes | No | - | The name of the timeline item. |
| label | string | Yes | Yes | - | The label of the timeline item. |
| type | timelineItemType | Yes | No | 'rating_tli' | The type of the timeline item. |
| themePrefix | string | Yes | No | - | The prefix to use when looking up theme values. |
| startTime | integer | Yes | No | - | The start time this timeline item appears on the timeline. |
| endTime | integer | Yes | No | - | The time the timeline item ends on the timeline. |
| startBehaviour | startBehaviour | Yes | No | pause, timer, continue, jump | What the player does when the start of the timeline item is reached. |
| endBehaviour | endBehaviour | Yes | No | pause, continue, loop | What the player does when the end of the timeline item is reached. |
| answerTime | integer | Yes | No | - | The amount of milliseconds the user has to answer the cue if 'timer' was selected for start behaviour. |
| timeoutMessage | timeoutMessage | Yes | No | - | Timeout message configuration. |
| background | background | Yes | No | - | Background to use for the timeline item. |
| showOverlay | boolean | Yes | Yes | - | True to show the overlay. |
| tags | tags | Yes | No | - | Tags associated with the timeline item. |
| showFeedback | boolean | Yes | No | - | True to show feedback after an answer. |
| showBreadcrumbs | boolean | Yes | No | - | True to show breadcrumbs on the feedback. |
| showPercentages | boolean | Yes | No | - | True to show percentages on the feedback. |
| feedbackMessage | string | Yes | Yes | - | The message to show on feedback. |
| layers | array(layer) | Yes | No | - | All layers available for the timeline item. |
| nodes | array(node) | Yes | No | - | All nodes within the timeline item. |

**Example:**
```json
{
  "id": 7,
  "name": "Rate Your Experience",
  "label": "How would you rate this?",
  "type": "rating_tli",
  "themePrefix": "default",
  "startTime": 60000,
  "endTime": 70000,
  "startBehaviour": "pause",
  "endBehaviour": "continue",
  "answerTime": 10000,
  "timeoutMessage": { "show": true, "text": "Please rate!" },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "showOverlay": true,
  "tags": ["rating"],
  "showFeedback": true,
  "showBreadcrumbs": false,
  "showPercentages": true,
  "feedbackMessage": "Thank you for your feedback!",
  "layers": [],
  "nodes": []
}
```

## 23.8 Ranking Cue Timeline Item (ranking_tli)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the timeline item. |
| name | string | Yes | No | - | The name of the timeline item. |
| label | string | Yes | Yes | - | The label of the timeline item. |
| type | timelineItemType | Yes | No | 'ranking_tli' | The type of the timeline item. |
| themePrefix | string | Yes | No | - | The prefix to use when looking up theme values. |
| startTime | integer | Yes | No | - | The start time this timeline item appears on the timeline. |
| endTime | integer | Yes | No | - | The time the timeline item ends on the timeline. |
| startBehaviour | startBehaviour | Yes | No | pause, timer, continue, jump | What the player does when the start of the timeline item is reached. |
| endBehaviour | endBehaviour | Yes | No | pause, continue, loop | What the player does when the end of the timeline item is reached. |
| answerTime | integer | Yes | No | - | The amount of milliseconds the user has to answer the cue if 'timer' was selected for start behaviour. |
| timeoutMessage | timeoutMessage | Yes | No | - | Timeout message configuration. |
| background | background | Yes | No | - | Background to use for the timeline item. |
| showOverlay | boolean | Yes | Yes | - | True to show the overlay. |
| tags | tags | Yes | No | - | Tags associated with the timeline item. |
| feedbackType | string | Yes | No | quiz, poll | The feedback type to display. |
| showFeedback | boolean | Yes | No | - | True to show feedback after an answer. |
| shuffleEnabled | boolean | Yes | No | - | True to enable shuffling of ranking items. |
| showBreadcrumbs | boolean | Yes | No | - | True to show breadcrumbs on the feedback. |
| showPercentages | boolean | Yes | No | - | True to show percentages on the feedback. |
| feedbackPollMessage | string | Yes | Yes | - | Message to show for poll feedback. |
| feedbackCorrectMessage | string | Yes | Yes | - | Message to show for correct answers. |
| feedbackIncorrectMessage | string | Yes | Yes | - | Message to show for incorrect answers. |
| layers | array(layer) | Yes | No | - | All layers available for the timeline item. |
| nodes | array(node) | Yes | No | - | All nodes within the timeline item. |

**Example:**
```json
{
  "id": 8,
  "name": "Rank the Options",
  "label": "Order these from best to worst:",
  "type": "ranking_tli",
  "themePrefix": "default",
  "startTime": 70000,
  "endTime": 80000,
  "startBehaviour": "timer",
  "endBehaviour": "pause",
  "answerTime": 15000,
  "timeoutMessage": { "show": true, "text": "Please rank!" },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "showOverlay": true,
  "tags": ["ranking"],
  "feedbackType": "quiz",
  "showFeedback": true,
  "shuffleEnabled": true,
  "showBreadcrumbs": false,
  "showPercentages": true,
  "feedbackPollMessage": "Most people ranked option A first.",
  "feedbackCorrectMessage": "Perfect order!",
  "feedbackIncorrectMessage": "Try again!",
  "layers": [],
  "nodes": []
}
```

## 23.9 Image Timeline Item (image_tli)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the timeline item. |
| name | string | Yes | No | - | The name of the timeline item. |
| label | string | Yes | Yes | - | The label of the timeline item. |
| type | timelineItemType | Yes | No | 'image_tli' | The type of the timeline item. |
| themePrefix | string | Yes | No | - | The prefix to use when looking up theme values. |
| startTime | integer | Yes | No | - | The start time this timeline item appears on the timeline. |
| endTime | integer | Yes | No | - | The time the timeline item ends on the timeline. |
| startBehaviour | startBehaviour | Yes | No | pause, timer, continue, jump | What the player does when the start of the timeline item is reached. |
| endBehaviour | endBehaviour | Yes | No | pause, continue, loop | What the player does when the end of the timeline item is reached. |
| answerTime | integer | Yes | No | - | The amount of milliseconds the user has to answer the cue if 'timer' was selected for start behaviour. |
| timeoutMessage | timeoutMessage | Yes | No | - | Timeout message configuration. |
| background | background | Yes | No | - | Background to use for the timeline item. |
| showOverlay | boolean | Yes | Yes | - | True to show the overlay. |
| tags | tags | Yes | No | - | Tags associated with the timeline item. |
| image | object | Yes | No | - | Object containing details of the image media to show. |
| image.x | unit | Yes | Yes | - | The x coordinate of the image. |
| image.y | unit | Yes | Yes | - | The y coordinate of the image. |
| image.width | unit | Yes | Yes | - | The width of the image. |
| image.height | unit | Yes | Yes | - | The height of the image. |
| image.source | imageMedia | Yes | No | - | The image media source. |
| layers | array(layer) | Yes | No | - | All layers available for the timeline item. |
| nodes | array(node) | Yes | No | - | All nodes within the timeline item. |

**Example:**
```json
{
  "id": 9,
  "name": "Show Image",
  "label": "Look at this image:",
  "type": "image_tli",
  "themePrefix": "default",
  "startTime": 80000,
  "endTime": 90000,
  "startBehaviour": "pause",
  "endBehaviour": "continue",
  "answerTime": 0,
  "timeoutMessage": { "show": false, "text": "" },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "showOverlay": false,
  "tags": ["image"],
  "image": {
    "x": "10%",
    "y": "10%",
    "width": "80%",
    "height": "80%",
    "source": {
      "id": null,
      "type": "image_media",
      "url": "https://cdn.example.com/img.png"
    }
  },
  "layers": [],
  "nodes": []
}
```

## 23.10 Video Timeline Item (video_tli)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the timeline item. |
| name | string | Yes | No | - | The name of the timeline item. |
| label | string | Yes | Yes | - | The label of the timeline item. |
| type | timelineItemType | Yes | No | 'video_tli' | The type of the timeline item. |
| themePrefix | string | Yes | No | - | The prefix to use when looking up theme values. |
| startTime | integer | Yes | No | - | The start time this timeline item appears on the timeline. |
| endTime | integer | Yes | No | - | The time the timeline item ends on the timeline. |
| startBehaviour | startBehaviour | Yes | No | pause, timer, continue, jump | What the player does when the start of the timeline item is reached. |
| endBehaviour | endBehaviour | Yes | No | pause, continue, loop | What the player does when the end of the timeline item is reached. |
| answerTime | integer | Yes | No | - | The amount of milliseconds the user has to answer the cue if 'timer' was selected for start behaviour. |
| timeoutMessage | timeoutMessage | Yes | No | - | Timeout message configuration. |
| background | background | Yes | No | - | Background to use for the timeline item. |
| showOverlay | boolean | Yes | Yes | - | True to show the overlay. |
| tags | tags | Yes | No | - | Tags associated with the timeline item. |
| video | object | Yes | No | - | Object containing details of the video media to show. |
| video.x | unit | Yes | Yes | - | The x coordinate of the video. |
| video.y | unit | Yes | Yes | - | The y coordinate of the video. |
| video.width | unit | Yes | Yes | - | The width of the video. |
| video.height | unit | Yes | Yes | - | The height of the video. |
| video.timeOffset | integer | Yes | No | - | The time offset for the video. |
| video.soundEnabled | boolean | Yes | No | - | True if sound is enabled. |
| video.baseVolume | integer | Yes | No | - | The base volume for the video. |
| video.source | videoMedia | Yes | No | - | The video media source. |
| layers | array(layer) | Yes | No | - | All layers available for the timeline item. |
| nodes | array(node) | Yes | No | - | All nodes within the timeline item. |

**Example:**
```json
{
  "id": 10,
  "name": "Show Video",
  "label": "Watch this video:",
  "type": "video_tli",
  "themePrefix": "default",
  "startTime": 90000,
  "endTime": 100000,
  "startBehaviour": "pause",
  "endBehaviour": "continue",
  "answerTime": 0,
  "timeoutMessage": { "show": false, "text": "" },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "showOverlay": false,
  "tags": ["video"],
  "video": {
    "x": "10%",
    "y": "10%",
    "width": "80%",
    "height": "80%",
    "timeOffset": 0,
    "soundEnabled": true,
    "baseVolume": 100,
    "source": {
      "id": null,
      "type": "video_media",
      "url": "https://cdn.example.com/video.mp4",
      "width": 1920,
      "height": 1080,
      "previewUrl": "https://cdn.example.com/preview.jpg",
      "previewFrameCount": 10,
      "previewFrameUrl": "https://cdn.example.com/frame.jpg"
    }
  },
  "layers": [],
  "nodes": []
}
```

## 23.11 Sound Timeline Item (sound_tli)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the timeline item. |
| name | string | Yes | No | - | The name of the timeline item. |
| label | string | Yes | Yes | - | The label of the timeline item. |
| type | timelineItemType | Yes | No | 'sound_tli' | The type of the timeline item. |
| themePrefix | string | Yes | No | - | The prefix to use when looking up theme values. |
| startTime | integer | Yes | No | - | The start time this timeline item appears on the timeline. |
| endTime | integer | Yes | No | - | The time the timeline item ends on the timeline. |
| startBehaviour | startBehaviour | Yes | No | pause, timer, continue, jump | What the player does when the start of the timeline item is reached. |
| endBehaviour | endBehaviour | Yes | No | pause, continue, loop | What the player does when the end of the timeline item is reached. |
| answerTime | integer | Yes | No | - | The amount of milliseconds the user has to answer the cue if 'timer' was selected for start behaviour. |
| timeoutMessage | timeoutMessage | Yes | No | - | Timeout message configuration. |
| background | background | Yes | No | - | Background to use for the timeline item. |
| showOverlay | boolean | Yes | Yes | - | True to show the overlay. |
| tags | tags | Yes | No | - | Tags associated with the timeline item. |
| sound | object | Yes | No | - | Object containing details of the sound to play. |
| sound.x | unit | Yes | Yes | - | The x coordinate of the sound node. |
| sound.y | unit | Yes | Yes | - | The y coordinate of the sound node. |
| sound.width | unit | Yes | Yes | - | The width of the sound node. |
| sound.height | unit | Yes | Yes | - | The height of the sound node. |
| sound.source | soundMedia | Yes | No | - | The sound media source. |
| layers | array(layer) | Yes | No | - | All layers available for the timeline item. |
| nodes | array(node) | Yes | No | - | All nodes within the timeline item. |

**Example:**
```json
{
  "id": 11,
  "name": "Play Sound",
  "label": "Listen to this sound:",
  "type": "sound_tli",
  "themePrefix": "default",
  "startTime": 100000,
  "endTime": 110000,
  "startBehaviour": "pause",
  "endBehaviour": "continue",
  "answerTime": 0,
  "timeoutMessage": { "show": false, "text": "" },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "showOverlay": false,
  "tags": ["sound"],
  "sound": {
    "x": "10%",
    "y": "10%",
    "width": "80%",
    "height": "80%",
    "source": {
      "id": null,
      "type": "sound_media",
      "url": "https://cdn.example.com/sound.mp3",
      "waveformUrl": "https://cdn.example.com/waveform.png"
    }
  },
  "layers": [],
  "nodes": []
}
```

## 23.12 Goto Timeline Item (goto_tli)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the timeline item. |
| name | string | Yes | No | - | The name of the timeline item. |
| label | string | Yes | Yes | - | The label of the timeline item. |
| type | timelineItemType | Yes | No | 'goto_tli' | The type of the timeline item. |
| themePrefix | string | Yes | No | - | The prefix to use when looking up theme values. |
| startTime | integer | Yes | No | - | The start time this timeline item appears on the timeline. |
| endTime | integer | Yes | No | - | The time the timeline item ends on the timeline. |
| startBehaviour | startBehaviour | Yes | No | pause, timer, continue, jump | What the player does when the start of the timeline item is reached. |
| endBehaviour | endBehaviour | Yes | No | pause, continue, loop | What the player does when the end of the timeline item is reached. |
| answerTime | integer | Yes | No | - | The amount of milliseconds the user has to answer the cue if 'timer' was selected for start behaviour. |
| timeoutMessage | timeoutMessage | Yes | No | - | Timeout message configuration. |
| background | background | Yes | No | - | Background to use for the timeline item. |
| showOverlay | boolean | Yes | Yes | - | True to show the overlay. |
| tags | tags | Yes | No | - | Tags associated with the timeline item. |
| marker | object | Yes | No | - | Object containing details of the marker to jump to. |
| marker.timelineId | integer | Yes | Yes | - | The ID of the timeline to jump to. |
| marker.time | integer | Yes | Yes | - | The time to jump to within the timeline in ms. |
| marker.trackIndex | integer | Yes | Yes | - | The track within the timeline. |
| marker.linkedTimelineItemId | integer | Yes | Yes | - | The timeline linked to the marker if split. |
| layers | array(layer) | Yes | No | - | All layers available for the timeline item. |
| nodes | array(node) | Yes | No | - | All nodes within the timeline item. |

**Example:**
```json
{
  "id": 12,
  "name": "Go To Marker",
  "label": "Jump to another point:",
  "type": "goto_tli",
  "themePrefix": "default",
  "startTime": 110000,
  "endTime": 120000,
  "startBehaviour": "jump",
  "endBehaviour": "pause",
  "answerTime": 0,
  "timeoutMessage": { "show": false, "text": "" },
  "background": { "color": "#FFBBCC00", "image": null, "video": null, "x": "50%", "y": "auto", "width": "100%", "height": "100%", "repeat": true },
  "showOverlay": false,
  "tags": ["goto"],
  "marker": {
    "timelineId": 2,
    "time": 5000,
    "trackIndex": 1,
    "linkedTimelineItemId": 5
  },
  "layers": [],
  "nodes": []
}
```

<!-- Continue with all other timeline item subtypes and all node subtypes, each with a full table and example. -->

## 24.1 Title Node (title_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | No | - | The name of the node. |
| type | string | Yes | No | 'title_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | No | - | The node's content. |
| contentAlign | string | Yes | No | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | unit | Yes | No | - | The width of the node. |
| height | unit | Yes | No | - | The height of the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |

**Example:**
```json
{
  "id": 101,
  "name": "Title",
  "type": "title_node",
  "themePrefix": "default",
  "content": "Welcome to the Experience!",
  "contentAlign": "center center",
  "value": null,
  "x": "10%",
  "y": "5%",
  "width": "80%",
  "height": "10%",
  "hoverStyle": {"background": {"color": "#EEEEEEFF"}},
  "selectedStyle": {"background": {"color": "#CCCCCCFF"}},
  "action": {"name": "none"},
  "animation": {"start": {"name": "bounce", "duration": 1000, "iterationCount": 1, "direction": "normal"}, "loop": {"name": "none", "duration": 0, "direction": "normal"}},
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0
}
```

## 24.2 Label Node (label_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | No | - | The name of the node. |
| type | string | Yes | No | 'label_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | No | - | The node's content. |
| contentAlign | string | Yes | No | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | unit | Yes | No | - | The width of the node. |
| height | unit | Yes | No | - | The height of the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |

**Example:**
```json
{
  "id": 102,
  "name": "Label",
  "type": "label_node",
  "themePrefix": "default",
  "content": "This is a label node.",
  "contentAlign": "center center",
  "value": null,
  "x": "10%",
  "y": "20%",
  "width": "80%",
  "height": "10%",
  "hoverStyle": {"background": {"color": "#EEEEEEFF"}},
  "selectedStyle": {"background": {"color": "#CCCCCCFF"}},
  "action": {"name": "none"},
  "animation": {"start": {"name": "bounce", "duration": 1000, "iterationCount": 1, "direction": "normal"}, "loop": {"name": "none", "duration": 0, "direction": "normal"}},
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0
}
```

## 24.3 Answer Timer Node (answer_timer_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | No | - | The name of the node. |
| type | string | Yes | No | 'answer_timer_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | No | - | The node's content. |
| contentAlign | string | Yes | No | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | unit | Yes | No | - | The width of the node. |
| height | unit | Yes | No | - | The height of the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |

**Example:**
```json
{
  "id": 103,
  "name": "Answer Timer",
  "type": "answer_timer_node",
  "themePrefix": "default",
  "content": "Time left: 10s",
  "contentAlign": "center center",
  "value": null,
  "x": "10%",
  "y": "30%",
  "width": "80%",
  "height": "10%",
  "hoverStyle": {"background": {"color": "#EEEEEEFF"}},
  "selectedStyle": {"background": {"color": "#CCCCCCFF"}},
  "action": {"name": "none"},
  "animation": {"start": {"name": "bounce", "duration": 1000, "iterationCount": 1, "direction": "normal"}, "loop": {"name": "none", "duration": 0, "direction": "normal"}},
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0
}
```

## 24.4 Timeout Message Node (timeout_message_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | No | - | The name of the node. |
| type | string | Yes | No | 'timeout_message_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | No | - | The node's content. |
| contentAlign | string | Yes | No | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | unit | Yes | No | - | The width of the node. |
| height | unit | Yes | No | - | The height of the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |

**Example:**
```json
{
  "id": 104,
  "name": "Timeout Message",
  "type": "timeout_message_node",
  "themePrefix": "default",
  "content": "Time's up!",
  "contentAlign": "center center",
  "value": null,
  "x": "10%",
  "y": "40%",
  "width": "80%",
  "height": "10%",
  "hoverStyle": {"background": {"color": "#EEEEEEFF"}},
  "selectedStyle": {"background": {"color": "#CCCCCCFF"}},
  "action": {"name": "none"},
  "animation": {"start": {"name": "bounce", "duration": 1000, "iterationCount": 1, "direction": "normal"}, "loop": {"name": "none", "duration": 0, "direction": "normal"}},
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0
}
```

## 24.5 Image Node (image_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | No | - | The name of the node. |
| type | string | Yes | No | 'image_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | No | - | The node's content. |
| contentAlign | string | Yes | No | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | unit | Yes | No | - | The width of the node. |
| height | unit | Yes | No | - | The height of the node. |
| image | imageMedia | Yes | No | - | The image media for the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |

**Example:**
```json
{
  "id": 105,
  "name": "Image",
  "type": "image_node",
  "themePrefix": "default",
  "content": "",
  "contentAlign": "center center",
  "value": null,
  "x": "10%",
  "y": "50%",
  "width": "80%",
  "height": "20%",
  "image": {
    "id": null,
    "type": "image_media",
    "url": "https://cdn.example.com/img.png"
  },
  "hoverStyle": {"background": {"color": "#EEEEEEFF"}},
  "selectedStyle": {"background": {"color": "#CCCCCCFF"}},
  "action": {"name": "none"},
  "animation": {"start": {"name": "bounce", "duration": 1000, "iterationCount": 1, "direction": "normal"}, "loop": {"name": "none", "duration": 0, "direction": "normal"}},
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0
}
```

## 24.6 Yes Node (yes_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | No | - | The name of the node. |
| type | string | Yes | No | 'yes_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | No | - | The node's content. |
| contentAlign | string | Yes | No | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | unit | Yes | No | - | The width of the node. |
| height | unit | Yes | No | - | The height of the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |

**Example:**
```json
{
  "id": 106,
  "name": "Yes",
  "type": "yes_node",
  "themePrefix": "default",
  "content": "Yes",
  "contentAlign": "center center",
  "value": null,
  "x": "10%",
  "y": "60%",
  "width": "35%",
  "height": "10%",
  "hoverStyle": {"background": {"color": "#EEEEEEFF"}},
  "selectedStyle": {"background": {"color": "#CCCCCCFF"}},
  "action": {"name": "none"},
  "animation": {"start": {"name": "bounce", "duration": 1000, "iterationCount": 1, "direction": "normal"}, "loop": {"name": "none", "duration": 0, "direction": "normal"}},
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0
}
```

## 24.7 No Node (no_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | No | - | The name of the node. |
| type | string | Yes | No | 'no_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | No | - | The node's content. |
| contentAlign | string | Yes | No | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | unit | Yes | No | - | The width of the node. |
| height | unit | Yes | No | - | The height of the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |

**Example:**
```json
{
  "id": 107,
  "name": "No",
  "type": "no_node",
  "themePrefix": "default",
  "content": "No",
  "contentAlign": "center center",
  "value": null,
  "x": "55%",
  "y": "60%",
  "width": "35%",
  "height": "10%",
  "hoverStyle": {"background": {"color": "#EEEEEEFF"}},
  "selectedStyle": {"background": {"color": "#CCCCCCFF"}},
  "action": {"name": "none"},
  "animation": {"start": {"name": "bounce", "duration": 1000, "iterationCount": 1, "direction": "normal"}, "loop": {"name": "none", "duration": 0, "direction": "normal"}},
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0
}
```

## 24.8 Button Node (button_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | Yes | - | The name of the node. |
| type | string | Yes | No | 'button_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | Yes | - | The node's content. |
| contentAlign | string | Yes | Yes | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | nodeSize | Yes | No | - | The width of the node. |
| height | nodeSize | Yes | No | - | The height of the node. |
| align | nodeAlign | Yes | No | top left, top center, top right, center left, center center, center right, bottom left, bottom center, bottom right | How the node should be aligned to its x and y coordinates. |
| font | font | Yes | No | - | Font configuration. |
| wordBreak | wordBreak | Yes | No | normal, break-all, keep-all, break-word, initial, inherit | Word break setting for content. |
| padding | padding | Yes | Yes | - | Content padding. |
| tags | tags | Yes | No | - | Tags associated with the node. |
| zIndex | integer | Yes | No | - | The z-index of the node. |
| background | background | Yes | No | - | Background configuration. |
| border | border | Yes | No | - | Border configuration. |
| opacity | opacity | Yes | Yes | - | The opacity of the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| hoverStyle.opacity | opacity | Yes | Yes | - | Opacity on hover. |
| hoverStyle.background | object | Yes | No | - | Background on hover. |
| hoverStyle.background.color | color | Yes | Yes | 8-digit hex | Hover background color. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| selectedStyle.opacity | opacity | Yes | Yes | - | Opacity when selected. |
| selectedStyle.background | object | Yes | No | - | Background when selected. |
| selectedStyle.background.color | color | Yes | Yes | 8-digit hex | Selected background color. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |

**Example:**
```json
{
  "id": 201,
  "name": "Button",
  "type": "button_node",
  "themePrefix": "default",
  "content": "Click Me!",
  "contentAlign": "center center",
  "value": null,
  "x": "20%",
  "y": "30%",
  "width": "60%",
  "height": "10%",
  "align": "center center",
  "font": { "color": "#000000FF", "family": "Arial", "size": 14, "weight": "bold", "style": "normal", "textDecoration": "none" },
  "wordBreak": "normal",
  "padding": "8px 16px",
  "tags": ["cta", "main"],
  "zIndex": 1,
  "background": { "color": "#FFDD00FF", "image": null, "video": null, "x": "0", "y": "0", "width": "100%", "height": "100%", "repeat": false },
  "border": { "color": "#000000FF", "style": "solid", "width": 1, "radius": 4 },
  "opacity": 1.0,
  "hoverStyle": { "opacity": 0.9, "background": { "color": "#FFE066FF" } },
  "selectedStyle": { "opacity": 1.0, "background": { "color": "#FFD700FF" } },
  "action": { "name": "jump", "marker": { "timelineId": 2, "time": 10000, "trackIndex": 0, "linkedTimelineItemId": null }, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 500, "iterationCount": 1, "direction": "normal" }, "loop": { "name": "none", "duration": 0, "direction": "normal" } },
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0
}
```

## 24.9 Submit Node (submit_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | Yes | - | The name of the node. |
| type | string | Yes | No | 'submit_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | Yes | - | The node's content. |
| contentAlign | string | Yes | Yes | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | nodeSize | Yes | No | - | The width of the node. |
| height | nodeSize | Yes | No | - | The height of the node. |
| align | nodeAlign | Yes | No | top left, top center, top right, center left, center center, center right, bottom left, bottom center, bottom right | How the node should be aligned to its x and y coordinates. |
| font | font | Yes | No | - | Font configuration. |
| wordBreak | wordBreak | Yes | No | normal, break-all, keep-all, break-word, initial, inherit | Word break setting for content. |
| padding | padding | Yes | Yes | - | Content padding. |
| tags | tags | Yes | No | - | Tags associated with the node. |
| zIndex | integer | Yes | No | - | The z-index of the node. |
| background | background | Yes | No | - | Background configuration. |
| border | border | Yes | No | - | Border configuration. |
| opacity | opacity | Yes | Yes | - | The opacity of the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| hoverStyle.opacity | opacity | Yes | Yes | - | Opacity on hover. |
| hoverStyle.background | object | Yes | No | - | Background on hover. |
| hoverStyle.background.color | color | Yes | Yes | 8-digit hex | Hover background color. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| selectedStyle.opacity | opacity | Yes | Yes | - | Opacity when selected. |
| selectedStyle.background | object | Yes | No | - | Background when selected. |
| selectedStyle.background.color | color | Yes | Yes | 8-digit hex | Selected background color. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |

**Example:**
```json
{
  "id": 202,
  "name": "Submit",
  "type": "submit_node",
  "themePrefix": "default",
  "content": "Submit Answer",
  "contentAlign": "center center",
  "value": null,
  "x": "20%",
  "y": "45%",
  "width": "60%",
  "height": "10%",
  "align": "center center",
  "font": { "color": "#FFFFFF", "family": "Arial", "size": 14, "weight": "bold", "style": "normal", "textDecoration": "none" },
  "wordBreak": "normal",
  "padding": "8px 16px",
  "tags": ["submit", "main"],
  "zIndex": 2,
  "background": { "color": "#007BFF", "image": null, "video": null, "x": "0", "y": "0", "width": "100%", "height": "100%", "repeat": false },
  "border": { "color": "#0056b3", "style": "solid", "width": 1, "radius": 4 },
  "opacity": 1.0,
  "hoverStyle": { "opacity": 0.95, "background": { "color": "#0056b3" } },
  "selectedStyle": { "opacity": 1.0, "background": { "color": "#003366" } },
  "action": { "name": "submit", "marker": null, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 500, "iterationCount": 1, "direction": "normal" }, "loop": { "name": "none", "duration": 0, "direction": "normal" } },
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0
}
```

## 24.10 Option Node (option_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | Yes | - | The name of the node. |
| type | string | Yes | No | 'option_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | Yes | - | The node's content. |
| contentAlign | string | Yes | Yes | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | nodeSize | Yes | No | - | The width of the node. |
| height | nodeSize | Yes | No | - | The height of the node. |
| align | nodeAlign | Yes | No | top left, top center, top right, center left, center center, center right, bottom left, bottom center, bottom right | How the node should be aligned to its x and y coordinates. |
| font | font | Yes | No | - | Font configuration. |
| wordBreak | wordBreak | Yes | No | normal, break-all, keep-all, break-word, initial, inherit | Word break setting for content. |
| padding | padding | Yes | Yes | - | Content padding. |
| tags | tags | Yes | No | - | Tags associated with the node. |
| zIndex | integer | Yes | No | - | The z-index of the node. |
| background | background | Yes | No | - | Background configuration. |
| border | border | Yes | No | - | Border configuration. |
| opacity | opacity | Yes | Yes | - | The opacity of the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| hoverStyle.opacity | opacity | Yes | Yes | - | Opacity on hover. |
| hoverStyle.background | object | Yes | No | - | Background on hover. |
| hoverStyle.background.color | color | Yes | Yes | 8-digit hex | Hover background color. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| selectedStyle.opacity | opacity | Yes | Yes | - | Opacity when selected. |
| selectedStyle.background | object | Yes | No | - | Background when selected. |
| selectedStyle.background.color | color | Yes | Yes | 8-digit hex | Selected background color. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |

**Example:**
```json
{
  "id": 203,
  "name": "Option",
  "type": "option_node",
  "themePrefix": "default",
  "content": "Option 1",
  "contentAlign": "center center",
  "value": null,
  "x": "20%",
  "y": "60%",
  "width": "60%",
  "height": "10%",
  "align": "center center",
  "font": { "color": "#333333FF", "family": "Arial", "size": 14, "weight": "normal", "style": "normal", "textDecoration": "none" },
  "wordBreak": "normal",
  "padding": "8px 16px",
  "tags": ["option"],
  "zIndex": 3,
  "background": { "color": "#F0F0F0", "image": null, "video": null, "x": "0", "y": "0", "width": "100%", "height": "100%", "repeat": false },
  "border": { "color": "#CCCCCC", "style": "solid", "width": 1, "radius": 4 },
  "opacity": 1.0,
  "hoverStyle": { "opacity": 0.95, "background": { "color": "#E0E0E0" } },
  "selectedStyle": { "opacity": 1.0, "background": { "color": "#B0B0B0" } },
  "action": { "name": "select", "marker": null, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 500, "iterationCount": 1, "direction": "normal" }, "loop": { "name": "none", "duration": 0, "direction": "normal" } },
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0
}
```

## 24.11 Input Node (input_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | Yes | - | The name of the node. |
| type | string | Yes | No | 'input_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | Yes | - | The node's content. |
| contentAlign | string | Yes | Yes | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | nodeSize | Yes | No | - | The width of the node. |
| height | nodeSize | Yes | No | - | The height of the node. |
| align | nodeAlign | Yes | No | top left, top center, top right, center left, center center, center right, bottom left, bottom center, bottom right | How the node should be aligned to its x and y coordinates. |
| font | font | Yes | No | - | Font configuration. |
| wordBreak | wordBreak | Yes | No | normal, break-all, keep-all, break-word, initial, inherit | Word break setting for content. |
| padding | padding | Yes | Yes | - | Content padding. |
| tags | tags | Yes | No | - | Tags associated with the node. |
| zIndex | integer | Yes | No | - | The z-index of the node. |
| background | background | Yes | No | - | Background configuration. |
| border | border | Yes | No | - | Border configuration. |
| opacity | opacity | Yes | Yes | - | The opacity of the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| hoverStyle.opacity | opacity | Yes | Yes | - | Opacity on hover. |
| hoverStyle.background | object | Yes | No | - | Background on hover. |
| hoverStyle.background.color | color | Yes | Yes | 8-digit hex | Hover background color. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| selectedStyle.opacity | opacity | Yes | Yes | - | Opacity when selected. |
| selectedStyle.background | object | Yes | No | - | Background when selected. |
| selectedStyle.background.color | color | Yes | Yes | 8-digit hex | Selected background color. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |
| placeholderText | string | Yes | Yes | - | The text to display as a placeholder within the input. |

**Example:**
```json
{
  "id": 204,
  "name": "Input",
  "type": "input_node",
  "themePrefix": "default",
  "content": "Enter your answer",
  "contentAlign": "center center",
  "value": null,
  "x": "20%",
  "y": "75%",
  "width": "60%",
  "height": "10%",
  "align": "center center",
  "font": { "color": "#000000FF", "family": "Arial", "size": 14, "weight": "normal", "style": "normal", "textDecoration": "none" },
  "wordBreak": "normal",
  "padding": "8px 16px",
  "tags": ["input"],
  "zIndex": 4,
  "background": { "color": "#FFFFFF", "image": null, "video": null, "x": "0", "y": "0", "width": "100%", "height": "100%", "repeat": false },
  "border": { "color": "#CCCCCC", "style": "solid", "width": 1, "radius": 4 },
  "opacity": 1.0,
  "hoverStyle": { "opacity": 0.95, "background": { "color": "#F0F0F0" } },
  "selectedStyle": { "opacity": 1.0, "background": { "color": "#E0E0E0" } },
  "action": { "name": "input", "marker": null, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 500, "iterationCount": 1, "direction": "normal" }, "loop": { "name": "none", "duration": 0, "direction": "normal" } },
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0,
  "placeholderText": "Type here..."
}
```

<!-- Repeat for graph_node, rating_node, ranking_node, modal_node, reaction_node, audience_select_node, wheel_of_fortune_node, breadcrumbs_node, video_node, each with a full table and example. -->

## 24.12 Graph Node (graph_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | Yes | - | The name of the node. |
| type | string | Yes | No | 'graph_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | Yes | - | The node's content. |
| contentAlign | string | Yes | Yes | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | nodeSize | Yes | No | - | The width of the node. |
| height | nodeSize | Yes | No | - | The height of the node. |
| align | nodeAlign | Yes | No | top left, top center, top right, center left, center center, center right, bottom left, bottom center, bottom right | How the node should be aligned to its x and y coordinates. |
| font | font | Yes | No | - | Font configuration. |
| wordBreak | wordBreak | Yes | No | normal, break-all, keep-all, break-word, initial, inherit | Word break setting for content. |
| padding | padding | Yes | Yes | - | Content padding. |
| tags | tags | Yes | No | - | Tags associated with the node. |
| zIndex | integer | Yes | No | - | The z-index of the node. |
| background | background | Yes | No | - | Background configuration. |
| border | border | Yes | No | - | Border configuration. |
| opacity | opacity | Yes | Yes | - | The opacity of the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| hoverStyle.opacity | opacity | Yes | Yes | - | Opacity on hover. |
| hoverStyle.background | object | Yes | No | - | Background on hover. |
| hoverStyle.background.color | color | Yes | Yes | 8-digit hex | Hover background color. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| selectedStyle.opacity | opacity | Yes | Yes | - | Opacity when selected. |
| selectedStyle.background | object | Yes | No | - | Background when selected. |
| selectedStyle.background.color | color | Yes | Yes | 8-digit hex | Selected background color. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |
| poll | object | Yes | No | - | Poll style config: normal, selected (graphNodeElement). |
| quiz | object | Yes | No | - | Quiz style config: correct, incorrect, selectedCorrect, selectedIncorrect (graphNodeElement). |

**Example:**
```json
{
  "id": 205,
  "name": "Graph",
  "type": "graph_node",
  "themePrefix": "default",
  "content": "Graph Content",
  "contentAlign": "center center",
  "value": null,
  "x": "10%",
  "y": "10%",
  "width": "80%",
  "height": "30%",
  "align": "center center",
  "font": { "color": "#000000FF", "family": "Arial", "size": 14, "weight": "normal", "style": "normal", "textDecoration": "none" },
  "wordBreak": "normal",
  "padding": "8px 16px",
  "tags": ["graph"],
  "zIndex": 5,
  "background": { "color": "#F8F8F8", "image": null, "video": null, "x": "0", "y": "0", "width": "100%", "height": "100%", "repeat": false },
  "border": { "color": "#CCCCCC", "style": "solid", "width": 1, "radius": 4 },
  "opacity": 1.0,
  "hoverStyle": { "opacity": 0.95, "background": { "color": "#E0E0E0" } },
  "selectedStyle": { "opacity": 1.0, "background": { "color": "#B0B0B0" } },
  "action": { "name": "select", "marker": null, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 500, "iterationCount": 1, "direction": "normal" }, "loop": { "name": "none", "duration": 0, "direction": "normal" } },
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0,
  "poll": { "normal": {}, "selected": {} },
  "quiz": { "correct": {}, "incorrect": {}, "selectedCorrect": {}, "selectedIncorrect": {} }
}
```

<!-- Repeat for rating_node, ranking_node, modal_node, reaction_node, audience_select_node, wheel_of_fortune_node, breadcrumbs_node, video_node, each with a full table and example. -->

## 24.13 Rating Node (rating_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | Yes | - | The name of the node. |
| type | string | Yes | No | 'rating_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | Yes | - | The node's content. |
| contentAlign | string | Yes | Yes | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | nodeSize | Yes | No | - | The width of the node. |
| height | nodeSize | Yes | No | - | The height of the node. |
| align | nodeAlign | Yes | No | top left, top center, top right, center left, center center, center right, bottom left, bottom center, bottom right | How the node should be aligned to its x and y coordinates. |
| font | font | Yes | No | - | Font configuration. |
| wordBreak | wordBreak | Yes | No | normal, break-all, keep-all, break-word, initial, inherit | Word break setting for content. |
| padding | padding | Yes | Yes | - | Content padding. |
| tags | tags | Yes | No | - | Tags associated with the node. |
| zIndex | integer | Yes | No | - | The z-index of the node. |
| background | background | Yes | No | - | Background configuration. |
| border | border | Yes | No | - | Border configuration. |
| opacity | opacity | Yes | Yes | - | The opacity of the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| hoverStyle.opacity | opacity | Yes | Yes | - | Opacity on hover. |
| hoverStyle.background | object | Yes | No | - | Background on hover. |
| hoverStyle.background.color | color | Yes | Yes | 8-digit hex | Hover background color. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| selectedStyle.opacity | opacity | Yes | Yes | - | Opacity when selected. |
| selectedStyle.background | object | Yes | No | - | Background when selected. |
| selectedStyle.background.color | color | Yes | Yes | 8-digit hex | Selected background color. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |
| layout | layoutType | Yes | No | 1 (column), 2 (row) | The layout to use for the Rating Node. |
| ratingItems | array(ratingItem) | Yes | No | - | Array of ratingItem objects. |

**Example:**
```json
{
  "id": 206,
  "name": "Rating",
  "type": "rating_node",
  "themePrefix": "default",
  "content": "Rate this!",
  "contentAlign": "center center",
  "value": null,
  "x": "10%",
  "y": "45%",
  "width": "80%",
  "height": "10%",
  "align": "center center",
  "font": { "color": "#000000FF", "family": "Arial", "size": 14, "weight": "normal", "style": "normal", "textDecoration": "none" },
  "wordBreak": "normal",
  "padding": "8px 16px",
  "tags": ["rating"],
  "zIndex": 6,
  "background": { "color": "#FFF8DC", "image": null, "video": null, "x": "0", "y": "0", "width": "100%", "height": "100%", "repeat": false },
  "border": { "color": "#CCCCCC", "style": "solid", "width": 1, "radius": 4 },
  "opacity": 1.0,
  "hoverStyle": { "opacity": 0.95, "background": { "color": "#FFE4B5" } },
  "selectedStyle": { "opacity": 1.0, "background": { "color": "#FFD700" } },
  "action": { "name": "rate", "marker": null, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 500, "iterationCount": 1, "direction": "normal" }, "loop": { "name": "none", "duration": 0, "direction": "normal" } },
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0,
  "layout": 1,
  "ratingItems": []
}
```

<!-- Repeat for ranking_node, modal_node, reaction_node, audience_select_node, wheel_of_fortune_node, breadcrumbs_node, video_node, each with a full table and example. -->

## 24.14 Ranking Node (ranking_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | Yes | - | The name of the node. |
| type | string | Yes | No | 'ranking_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | Yes | - | The node's content. |
| contentAlign | string | Yes | Yes | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | nodeSize | Yes | No | - | The width of the node. |
| height | nodeSize | Yes | No | - | The height of the node. |
| align | nodeAlign | Yes | No | top left, top center, top right, center left, center center, center right, bottom left, bottom center, bottom right | How the node should be aligned to its x and y coordinates. |
| font | font | Yes | No | - | Font configuration. |
| wordBreak | wordBreak | Yes | No | normal, break-all, keep-all, break-word, initial, inherit | Word break setting for content. |
| padding | padding | Yes | Yes | - | Content padding. |
| tags | tags | Yes | No | - | Tags associated with the node. |
| zIndex | integer | Yes | No | - | The z-index of the node. |
| background | background | Yes | No | - | Background configuration. |
| border | border | Yes | No | - | Border configuration. |
| opacity | opacity | Yes | Yes | - | The opacity of the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| hoverStyle.opacity | opacity | Yes | Yes | - | Opacity on hover. |
| hoverStyle.background | object | Yes | No | - | Background on hover. |
| hoverStyle.background.color | color | Yes | Yes | 8-digit hex | Hover background color. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| selectedStyle.opacity | opacity | Yes | Yes | - | Opacity when selected. |
| selectedStyle.background | object | Yes | No | - | Background when selected. |
| selectedStyle.background.color | color | Yes | Yes | 8-digit hex | Selected background color. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |
| layout | layoutType | Yes | No | 1 (column), 2 (row) | The layout to use for the Ranking Node. |
| rankingItems | array(rankingItem) | Yes | No | - | Array of rankingItem objects. |

**Example:**
```json
{
  "id": 207,
  "name": "Ranking",
  "type": "ranking_node",
  "themePrefix": "default",
  "content": "Rank these items!",
  "contentAlign": "center center",
  "value": null,
  "x": "10%",
  "y": "60%",
  "width": "80%",
  "height": "10%",
  "align": "center center",
  "font": { "color": "#000000FF", "family": "Arial", "size": 14, "weight": "normal", "style": "normal", "textDecoration": "none" },
  "wordBreak": "normal",
  "padding": "8px 16px",
  "tags": ["ranking"],
  "zIndex": 7,
  "background": { "color": "#F0FFF0", "image": null, "video": null, "x": "0", "y": "0", "width": "100%", "height": "100%", "repeat": false },
  "border": { "color": "#CCCCCC", "style": "solid", "width": 1, "radius": 4 },
  "opacity": 1.0,
  "hoverStyle": { "opacity": 0.95, "background": { "color": "#E0FFE0" } },
  "selectedStyle": { "opacity": 1.0, "background": { "color": "#B0FFB0" } },
  "action": { "name": "rank", "marker": null, "url": null, "openInNewTab": false, "modalLayer": null },
  "animation": { "start": { "name": "bounce", "duration": 500, "iterationCount": 1, "direction": "normal" }, "loop": { "name": "none", "duration": 0, "direction": "normal" } },
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0,
  "layout": 1,
  "rankingItems": []
}
```

<!-- Repeat for modal_node, reaction_node, audience_select_node, wheel_of_fortune_node, breadcrumbs_node, video_node, each with a full table and example. -->

## 24.15 Modal Node (modal_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | Yes | - | The name of the node. |
| type | string | Yes | No | 'modal_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | Yes | - | The node's content. |
| contentAlign | string | Yes | Yes | top left, top center, top right, top justify, center left, center center, center right, center justify, bottom left, bottom center, bottom right, bottom justify | How to align the content within the node. |
| value | string | Yes | Yes | - | The value of the node. |
| x | unit | Yes | No | - | The x coordinate of the node. |
| y | unit | Yes | No | - | The y coordinate of the node. |
| width | nodeSize | Yes | No | - | The width of the node. |
| height | nodeSize | Yes | No | - | The height of the node. |
| align | nodeAlign | Yes | No | top left, top center, top right, center left, center center, center right, bottom left, bottom center, bottom right | How the node should be aligned to its x and y coordinates. |
| font | font | Yes | No | - | Font configuration. |
| wordBreak | wordBreak | Yes | No | normal, break-all, keep-all, break-word, initial, inherit | Word break setting for content. |
| padding | padding | Yes | Yes | - | Content padding. |
| tags | tags | Yes | No | - | Tags associated with the node. |
| zIndex | integer | Yes | No | - | The z-index of the node. |
| background | background | Yes | No | - | Background configuration. |
| border | border | Yes | No | - | Border configuration. |
| opacity | opacity | Yes | Yes | - | The opacity of the node. |
| hoverStyle | object | Yes | No | - | Style when the node is hovered. |
| hoverStyle.opacity | opacity | Yes | Yes | - | Opacity on hover. |
| hoverStyle.background | object | Yes | No | - | Background on hover. |
| hoverStyle.background.color | color | Yes | Yes | 8-digit hex | Hover background color. |
| selectedStyle | object | Yes | No | - | Style when the node is selected. |
| selectedStyle.opacity | opacity | Yes | Yes | - | Opacity when selected. |
| selectedStyle.background | object | Yes | No | - | Background when selected. |
| selectedStyle.background.color | color | Yes | Yes | 8-digit hex | Selected background color. |
| action | action | Yes | No | - | Action when the node is clicked. |
| animation | animation | Yes | No | - | Animation to apply to the node. |
| isMovable | boolean | Yes | No | - | True if the node can be moved. |
| isSizeable | boolean | Yes | No | - | True if the node can be resized. |
| isDeletable | boolean | Yes | No | - | True if the node can be deleted. |
| isDuplicatable | boolean | Yes | No | - | True if the node can be duplicated. |
| isEditable | boolean | Yes | No | - | True if the node's content can be edited. |
| isRequired | boolean | Yes | No | - | True if the node is required. |
| allowActionChange | boolean | Yes | No | - | True if the action can be changed. |
| isHidden | boolean | Yes | No | - | True if the node is hidden. |
| isSelectable | boolean | Yes | No | - | True if the node can be selected. |
| isMuted | boolean | Yes | No | - | True if the node's content should be muted. |
| showFeedback | boolean | Yes | No | - | True if the node can be used to show feedback. |
| feedbackMessage | string | Yes | Yes | - | The feedback message to show. |
| aspectRatio | number | Yes | Yes | - | The aspect ratio of the node. |
| shape | string | Yes | No | rectangle, square, circle, ellipse | The shape of the node. |
| audienceId | string | Yes | Yes | - | The ID of the audience if used for audience selection. |
| layer | integer | Yes | No | - | The index of the layer this node belongs to. |

**Example:**
```json
{
  "id": 208,
  "name": "Modal",
  "type": "modal_node",
  "themePrefix": "default",
  "content": "This is a modal dialog.",
  "contentAlign": "center center",
  "value": null,
  "x": "30%",
  "y": "30%",
  "width": "40%",
  "height": "20%",
  "align": "center center",
  "font": { "color": "#000000FF", "family": "Arial", "size": 14, "weight": "normal", "style": "normal", "textDecoration": "none" },
  "wordBreak": "normal",
  "padding": "8px 16px",
  "tags": ["modal"],
  "zIndex": 8,
  "background": { "color": "#FFFFFF", "image": null, "video": null, "x": "0", "y": "0", "width": "100%", "height": "100%", "repeat": false },
  "border": { "color": "#CCCCCC", "style": "solid", "width": 1, "radius": 4 },
  "opacity": 1.0,
  "hoverStyle": { "opacity": 0.95, "background": { "color": "#F0F0F0" } },
  "selectedStyle": { "opacity": 1.0, "background": { "color": "#E0E0E0" } },
  "action": { "name": "open_modal", "marker": null, "url": null, "openInNewTab": false, "modalLayer": 1 },
  "animation": { "start": { "name": "bounce", "duration": 500, "iterationCount": 1, "direction": "normal" }, "loop": { "name": "none", "duration": 0, "direction": "normal" } },
  "isMovable": true,
  "isSizeable": true,
  "isDeletable": true,
  "isDuplicatable": true,
  "isEditable": true,
  "isRequired": false,
  "allowActionChange": true,
  "isHidden": false,
  "isSelectable": true,
  "isMuted": false,
  "showFeedback": false,
  "feedbackMessage": null,
  "aspectRatio": null,
  "shape": "rectangle",
  "audienceId": null,
  "layer": 0
}
```

<!-- Repeat for reaction_node, audience_select_node, wheel_of_fortune_node, breadcrumbs_node, video_node, each with a full table and example. -->

## 24.16 Reaction Node (reaction_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | Yes | - | The name of the node. |
| type | string | Yes | No | 'reaction_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | Yes | - | The node's content. |
| reactions | array of strings | Yes | No | - | List of allowed reactions. |
| next | integer | Yes | No | - | The ID of the next node. |
| flags | object | No | Yes | - | Optional flags for the node. |

**Example:**
```json
{
  "id": 1601,
  "name": "Reaction Node Example",
  "type": "reaction_node",
  "themePrefix": "default",
  "content": "How do you feel about this?",
  "reactions": ["👍", "👎", "😐"],
  "next": 1602,
  "flags": {
    "skippable": true
  }
}
```

---

## 24.17 Audience Select Node (audience_select_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | Yes | - | The name of the node. |
| type | string | Yes | No | 'audience_select_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | Yes | - | The node's content. |
| options | array of objects | Yes | No | - | List of audience options. Each option is an object with `id`, `label`, and `value`. |
| next | integer | Yes | No | - | The ID of the next node. |
| flags | object | No | Yes | - | Optional flags for the node. |

**Example:**
```json
{
  "id": 1701,
  "name": "Audience Select Node Example",
  "type": "audience_select_node",
  "themePrefix": "default",
  "content": "Select your group:",
  "options": [
    {"id": 1, "label": "Students", "value": "students"},
    {"id": 2, "label": "Teachers", "value": "teachers"}
  ],
  "next": 1702,
  "flags": {
    "skippable": false
  }
}
```

---

## 24.18 Wheel of Fortune Node (wheel_of_fortune_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | Yes | - | The name of the node. |
| type | string | Yes | No | 'wheel_of_fortune_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | Yes | - | The node's content. |
| segments | array of objects | Yes | No | - | List of wheel segments. Each segment is an object with `id`, `label`, and `value`. |
| next | integer | Yes | No | - | The ID of the next node. |
| flags | object | No | Yes | - | Optional flags for the node. |

**Example:**
```json
{
  "id": 1801,
  "name": "Wheel of Fortune Node Example",
  "type": "wheel_of_fortune_node",
  "themePrefix": "default",
  "content": "Spin the wheel!",
  "segments": [
    {"id": 1, "label": "Prize 1", "value": "p1"},
    {"id": 2, "label": "Prize 2", "value": "p2"}
  ],
  "next": 1802,
  "flags": {
    "skippable": false
  }
}
```

---

## 24.19 Breadcrumbs Node (breadcrumbs_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | Yes | - | The name of the node. |
| type | string | Yes | No | 'breadcrumbs_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | Yes | - | The node's content. |
| breadcrumbs | array of objects | Yes | No | - | List of breadcrumb items. Each item is an object with `label` and `nodeId`. |
| next | integer | Yes | No | - | The ID of the next node. |
| flags | object | No | Yes | - | Optional flags for the node. |

**Example:**
```json
{
  "id": 1901,
  "name": "Breadcrumbs Node Example",
  "type": "breadcrumbs_node",
  "themePrefix": "default",
  "content": "You are here:",
  "breadcrumbs": [
    {"label": "Start", "nodeId": 100},
    {"label": "Middle", "nodeId": 200}
  ],
  "next": 1902,
  "flags": {
    "skippable": true
  }
}
```

---

## 24.20 Video Node (video_node)

| Field | Type | Required | Nullable | Allowed Values/Format | Description |
|-------|------|----------|----------|----------------------|-------------|
| id | integer | Yes | No | - | The ID of the node. |
| name | string | Yes | Yes | - | The name of the node. |
| type | string | Yes | No | 'video_node' | The type of the node. |
| themePrefix | string | Yes | No | - | The theme prefix to use when looking up styles. |
| content | string | Yes | Yes | - | The node's content. |
| videoUrl | string | Yes | No | URL | The URL of the video to display. |
| next | integer | Yes | No | - | The ID of the next node. |
| flags | object | No | Yes | - | Optional flags for the node. |

**Example:**
```json
{
  "id": 2001,
  "name": "Video Node Example",
  "type": "video_node",
  "themePrefix": "default",
  "content": "Watch this video:",
  "videoUrl": "https://example.com/video.mp4",
  "next": 2002,
  "flags": {
    "skippable": false
  }
}
```

</rewritten_file> 