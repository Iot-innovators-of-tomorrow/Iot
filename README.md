# Smart Home Assistant

An intelligent object detection system that helps locate items in your home using computer vision and Django/Flask integration.

## Visualisation

### Homepage

<img alt="homepage" src="./media/images/image copy 3.png" />

### Object selection page

<img alt="homepage" src="./media/images/image copy 2.png"/>

### Result Page

<img alt="homepage" src="./media/images/image.png"/>

### Image Not Found Page

<img alt="homepage" src="./media/images/image copy.png"/>

## System Architecture

```mermaid
graph TB
    U[User Interface] --> D[Django Backend]
    D --> F[Flask Server]
    F --> Y[YOLO Processing]
    Y --> C[Camera System]
    C --> I[Image Processing]
    I --> D
    
    subgraph Hardware
    C
    end
    
    subgraph Processing
    Y
    I
    end
    
    subgraph Web
    U
    D
    end
```

## How It Works

### Object Detection Pipeline

```mermaid
flowchart LR
    A[Camera Feed] --> B[Frame Capture]
    B --> C[YOLO Detection]
    C --> D{Object Found?}
    D -->|Yes| E[Capture Image]
    D -->|No| B
    E --> F[Send to Django]
```

### Django-Flask Communication

```mermaid
sequenceDiagram
    participant U as User
    participant D as Django
    participant F as Flask
    participant Y as YOLO
    
    U->>D: Search Request
    D->>F: Forward Request
    F->>Y: Activate Detection
    Y->>F: Object Found
    F->>D: Send Image
    D->>U: Display Result
```

### System Implementation

```mermaid
graph TD
    subgraph Web Layer
        A[Django Frontend]
        B[REST API]
    end
    
    subgraph Processing Layer
        C[Flask Server]
        D[YOLO Model]
    end
    
    subgraph Hardware Layer
        E[Cameras]
        F[Raspberry Pi]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> C
```

## API Documentation

### Flask Endpoints

```python
POST /search_object
{
    "item_name": "string",  // Object to search for
    "threshold": float,     // Detection confidence threshold
}
```

### Django Endpoints

```python
POST /receive_picture
{
    "image": file,         // Captured image
    "camera_index": int,   // Source camera ID
    "location": string     // Detection location
}
```

## Detection Process

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Searching: User Request
    Searching --> Processing: Frame Captured
    Processing --> ObjectFound: Detection Success
    Processing --> Searching: No Detection
    ObjectFound --> ImageCapture
    ImageCapture --> ResultDisplay
    ResultDisplay --> Idle
```

## Project Team

```mermaid
organizationChart
    CEO[Smart Home Assistant]
    B[Project Lead]
    C[Computer Vision]
    D[Web Development]
    E[Hardware Integration]

    CEO --> B
    B --> C
    B --> D
    B --> E

    B[Project Lead: Javokhir Yuldoshev]
    C[Computer Vision: Akimov Sarvar]
    D[Web Development: Azizbek Sharifov]
    E[Hardware Integration: Abdulloh Shabonov]
```
