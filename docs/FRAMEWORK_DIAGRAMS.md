# MCP Appium Framework Diagrams

This document contains diagrams that illustrate the architecture, components, and workflows of the MCP Appium framework.

## System Architecture

```mermaid
graph TB
    subgraph "MCP Appium Framework"
        MCP[MCP Server] --> |Controls| APP[Mobile App Testing]
        MCP --> |Controls| BRW[Browser Testing]
        MCP --> |Controls| API[API Testing]
        
        subgraph "Components"
            APP --> ACLI[Appium Client]
            BRW --> PCLI[Playwright Client]
            API --> OCLI[OpenAPI Client]
            
            ACLI --> |Native Mobile| AND[Android Testing]
            ACLI --> |Native Mobile| IOS[iOS Testing]
            PCLI --> |Web| WEB[Web Testing]
            OCLI --> |API| APIR[REST API Testing]
            
            AND --> |Generates| ROBOTM[Robot Mobile Test Scripts]
            IOS --> |Generates| ROBOTM
            WEB --> |Generates| ROBOTW[Robot Web Test Scripts]
            APIR --> |Generates| ROBOTA[Robot API Test Scripts]
        end
        
        subgraph "AI Integration"
            AI[AI Integration]
            AI --> OPENAI[OpenAI]
            AI --> GEMINI[Google Gemini]
            AI --> OLLAMA[Ollama Local LLM]
            AI --> HF[Hugging Face]
            
            AI --> |Enhances| APP
            AI --> |Enhances| BRW
            AI --> |Enhances| API
        end
        
        subgraph "Execution Environment"
            DOC[Docker Container]
            DOC --> APPIUM[Appium Server]
            DOC --> ANDROID[Android Emulator]
            DOC --> SERVER[MCP Application]
        end
    end
    
    CLI[Command Line Interface] --> MCP
    WUI[Web User Interface] --> MCP
    STUI[Streamlit UI] --> MCP
```

## User Workflow

```mermaid
flowchart TD
    START[Start] --> CHOOSE[Choose Testing Type]
    
    CHOOSE --> MOBILE[Mobile Testing]
    CHOOSE --> WEB[Web Testing]
    CHOOSE --> API[API Testing]
    
    MOBILE --> CONF_M[Configure Mobile Test]
    WEB --> CONF_W[Configure Web Test]
    API --> CONF_A[Configure API Test]
    
    CONF_M --> |Connect| APP[Connect to App/Device]
    CONF_W --> |Connect| BROWSER[Connect to Browser]
    CONF_A --> |Parse| SPEC[Parse OpenAPI Spec]
    
    APP --> AI_M[AI Analysis of App]
    BROWSER --> AI_W[AI Analysis of Web Page]
    SPEC --> AI_A[AI Analysis of API Endpoints]
    
    AI_M --> GEN_M[Generate Robot Test Scripts]
    AI_W --> GEN_W[Generate Robot Test Scripts]
    AI_A --> GEN_A[Generate Robot Test Scripts]
    
    GEN_M --> EXE_M[Execute Tests]
    GEN_W --> EXE_W[Execute Tests]
    GEN_A --> EXE_A[Execute Tests]
    
    EXE_M --> REPORT[Generate Reports]
    EXE_W --> REPORT
    EXE_A --> REPORT
    
    REPORT --> END[End]
```

## Mobile Testing Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as Command Line
    participant Server as MCP Server
    participant AI as AI Integration
    participant Appium as Appium Server
    participant Device as Mobile Device
    participant Robot as Robot Framework
    
    User->>CLI: Run mobile test command
    CLI->>Server: Start mobile testing session
    Server->>Appium: Connect to Appium server
    Appium->>Device: Start app on device
    Device-->>Appium: Return app session
    Appium-->>Server: Return connection status
    
    Server->>Device: Capture screen & XML
    Device-->>Server: Return screen data
    Server->>AI: Analyze screen structure
    AI-->>Server: Return element analysis
    
    alt AI Command Interpretation
        User->>CLI: Enter natural language command
        CLI->>Server: Forward command
        Server->>AI: Interpret command
        AI-->>Server: Return appium commands
        Server->>Appium: Execute commands
        Appium->>Device: Interact with app
    end
    
    alt Script Generation
        User->>CLI: Request test script
        CLI->>Server: Forward request
        Server->>AI: Generate test script
        AI-->>Server: Return Robot script
        Server-->>User: Save Robot script
    end
    
    alt Script Execution
        User->>Robot: Run generated script
        Robot->>Appium: Execute test steps
        Appium->>Device: Perform test actions
        Device-->>Appium: Return test results
        Appium-->>Robot: Return action status
        Robot-->>User: Generate test report
    end
```

## Web Testing Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as Command Line
    participant Server as MCP Server
    participant AI as AI Integration
    participant Playwright as Playwright
    participant Browser as Web Browser
    participant Robot as Robot Framework
    
    User->>CLI: Run web test command
    CLI->>Server: Start web testing session
    Server->>Playwright: Launch browser
    Playwright->>Browser: Open URL
    Browser-->>Playwright: Return page loaded
    Playwright-->>Server: Return connection status
    
    Server->>Browser: Capture page content
    Browser-->>Server: Return HTML content
    Server->>AI: Analyze page structure
    AI-->>Server: Return element analysis
    
    alt AI Command Interpretation
        User->>CLI: Enter natural language command
        CLI->>Server: Forward command
        Server->>AI: Interpret command
        AI-->>Server: Return browser commands
        Server->>Playwright: Execute commands
        Playwright->>Browser: Interact with page
    end
    
    alt Script Generation
        User->>CLI: Request test script
        CLI->>Server: Forward request
        Server->>AI: Generate test script
        AI-->>Server: Return Robot script
        Server-->>User: Save Robot script
    end
    
    alt Script Execution
        User->>Robot: Run generated script
        Robot->>Playwright: Execute test steps
        Playwright->>Browser: Perform test actions
        Browser-->>Playwright: Return test results
        Playwright-->>Robot: Return action status
        Robot-->>User: Generate test report
    end
```

## API Testing Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as Command Line
    participant Server as MCP Server
    participant Parser as OpenAPI Parser
    participant AI as AI Integration
    participant HTTP as HTTP Client
    participant API as API Server
    participant Robot as Robot Framework
    
    User->>CLI: Run API test command
    CLI->>Server: Start API testing session
    Server->>Parser: Parse OpenAPI spec
    Parser-->>Server: Return endpoints & schemas
    
    Server->>AI: Analyze API structure
    AI-->>Server: Return API analysis
    
    alt Endpoint Testing
        Server->>HTTP: Send request to endpoint
        HTTP->>API: Forward HTTP request
        API-->>HTTP: Return API response
        HTTP-->>Server: Return response data
    end
    
    alt Script Generation
        User->>CLI: Request test script
        CLI->>Server: Forward request
        Server->>AI: Generate test script
        AI-->>Server: Return Robot script
        Server-->>User: Save Robot script
    end
    
    alt Script Execution
        User->>Robot: Run generated script
        Robot->>HTTP: Execute test requests
        HTTP->>API: Send API requests
        API-->>HTTP: Return API responses
        HTTP-->>Robot: Return response data
        Robot-->>User: Generate test report
    end
```

## AI Integration Flow

```mermaid
flowchart TB
    subgraph "AI Integration"
        AI[AI Module] --> |Choose Provider| PROVIDER
        
        PROVIDER --> OPENAI[OpenAI Provider]
        PROVIDER --> GEMINI[Google Gemini Provider]
        PROVIDER --> OLLAMA[Ollama Provider]
        PROVIDER --> HF[Hugging Face Provider]
        
        OPENAI --> |API Key| GPT[GPT-4o Model]
        GEMINI --> |API Key| GEM[Gemini Pro Model]
        OLLAMA --> |Local| LOCAL[Local LLM]
        HF --> |API Key| HUGGING[HF Models]
        
        GPT --> TASKS
        GEM --> TASKS
        LOCAL --> TASKS
        HUGGING --> TASKS
        
        subgraph "AI Tasks"
            TASKS
            TASKS --> DESC[Screen Description]
            TASKS --> SUGGEST[Suggested Actions]
            TASKS --> INTERPRET[Command Interpretation]
            TASKS --> GEN[Test Script Generation]
            TASKS --> ANALYZE[UI/API Structure Analysis]
        end
    end
```

## Robot Framework Test Generation

```mermaid
flowchart TB
    subgraph "Robot Framework Test Generation"
        GEN[Test Generator] --> |Choose Type| TYPE
        
        TYPE --> WEBGEN[Web Test Generator]
        TYPE --> MOBGEN[Mobile Test Generator]
        TYPE --> APIGEN[API Test Generator]
        
        WEBGEN --> |Configure| WEBCONF[Web Configuration]
        MOBGEN --> |Configure| MOBCONF[Mobile Configuration]
        APIGEN --> |Configure| APICONF[API Configuration]
        
        WEBCONF --> |Browser Library| WEBSCRIPT[Generate Robot Web Script]
        MOBCONF --> |AppiumLibrary| MOBSCRIPT[Generate Robot Mobile Script]
        APICONF --> |RequestsLibrary| APISCRIPT[Generate Robot API Script]
        
        WEBSCRIPT --> |Save| OUTPUT[Output Robot File]
        MOBSCRIPT --> |Save| OUTPUT
        APISCRIPT --> |Save| OUTPUT
    end
```

## Docker Deployment Flow

```mermaid
flowchart TB
    subgraph "Docker Deployment"
        DOCKER[Docker Compose] --> |Start Services| SERVICES
        
        SERVICES --> APPIUM[Appium Service]
        SERVICES --> OLLAMA[Ollama Service]
        SERVICES --> MCP[MCP Server Service]
        
        APPIUM --> |Mounts| APPS[Mobile Apps Volume]
        APPIUM --> |Starts| EMU[Android Emulator]
        
        OLLAMA --> |Mounts| MODELS[LLM Models Volume]
        
        MCP --> |Connects to| APPIUM
        MCP --> |Connects to| OLLAMA
        MCP --> |Exposes Port| PORT[Port 5000]
        
        PORT --> |Access| WEB[Web Interface]
        PORT --> |Access| CLI[CLI Interface]
    end
```

## Usage Example: Mobile Test Generation

```mermaid
sequenceDiagram
    participant User
    participant CLI as Command Line
    participant Gen as Test Generator
    participant File as Robot File
    
    User->>CLI: python examples/generate_robot_tests.py --type mobile --app app_tests/sauce_labs_demo/sauce_labs_demo.apk --output data/generated_tests/mobile_tests.robot
    CLI->>Gen: Process command arguments
    Gen->>Gen: Initialize mobile test generator
    Gen->>Gen: Configure test parameters
    Gen->>Gen: Generate Robot Framework script
    Gen->>File: Save generated script
    File-->>User: Confirmation message
    
    User->>CLI: robot data/generated_tests/mobile_tests.robot
    CLI->>File: Execute Robot Framework test
    File-->>User: Test execution report
```

## Usage Example: Web Test Generation

```mermaid
sequenceDiagram
    participant User
    participant CLI as Command Line
    participant Gen as Test Generator
    participant File as Robot File
    
    User->>CLI: python examples/generate_robot_tests.py --type web --url https://www.saucedemo.com/ --output data/generated_tests/web_tests.robot
    CLI->>Gen: Process command arguments
    Gen->>Gen: Initialize web test generator
    Gen->>Gen: Configure test parameters
    Gen->>Gen: Generate Robot Framework script
    Gen->>File: Save generated script
    File-->>User: Confirmation message
    
    User->>CLI: robot data/generated_tests/web_tests.robot
    CLI->>File: Execute Robot Framework test
    File-->>User: Test execution report
```

## Usage Example: API Test Generation

```mermaid
sequenceDiagram
    participant User
    participant CLI as Command Line
    participant Gen as Test Generator
    participant File as Robot File
    
    User->>CLI: python examples/api_testing_example.py --spec data/api_specs/petstore_spec.json --output data/generated_tests/api_tests.robot
    CLI->>Gen: Process command arguments
    Gen->>Gen: Parse OpenAPI specification
    Gen->>Gen: Configure test parameters
    Gen->>Gen: Generate Robot Framework script
    Gen->>File: Save generated script
    File-->>User: Confirmation message
    
    User->>CLI: robot data/generated_tests/api_tests.robot
    CLI->>File: Execute Robot Framework test
    File-->>User: Test execution report
```