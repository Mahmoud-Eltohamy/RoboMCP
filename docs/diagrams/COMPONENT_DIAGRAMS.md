# MCP Appium Component Diagrams

This document contains detailed component diagrams for the MCP Appium framework.

## Main Components Interaction

```mermaid
graph TB
    subgraph "MCP Appium Core Components"
        SERVER[MCP Server] --- CLIENT[MCP Client]
        SERVER --- AI[AI Integration]
        CLIENT --- APPIUM[Appium Client]
        CLIENT --- BROWSER[Browser Client]
        CLIENT --- API[API Client]
        
        APPIUM --- ELEMENT_M[Mobile Element]
        BROWSER --- ELEMENT_W[Web Element]
        API --- OPENAPI[OpenAPI Parser]
        
        OPENAPI --- ROBOT_GEN[Robot Generator]
        ELEMENT_M --- ROBOT_MOB[Robot Mobile Generator]
        ELEMENT_W --- ROBOT_WEB[Robot Web Generator]
    end
```

## AI Integration Component Detail

```mermaid
classDiagram
    class MCPAIIntegration {
        +ai_provider: AIProvider
        +model_name: str
        +temperature: float
        +max_tokens: int
        +retry_count: int
        +retry_delay: float
        +timeout: int
        +describe_screen(screenshot, page_source)
        +suggest_test_actions(screenshot, page_source)
        +interpret_command(command, context)
        +generate_test_script(test_goal, language)
        +analyze_app_structure(app_info)
    }
    
    class AIProvider {
        <<enumeration>>
        OPENAI
        GOOGLE
        HUGGING_FACE
        OLLAMA
    }
    
    class OpenAIProvider {
        -api_key: str
        -client: OpenAI
        +call_model(prompt, params)
        -handle_api_error(error)
    }
    
    class GoogleProvider {
        -api_key: str
        -client: genai.GenerativeModel
        +call_model(prompt, params)
        -handle_api_error(error)
    }
    
    class OllamaProvider {
        -host: str
        -port: int
        +call_model(prompt, params)
        -handle_api_error(error)
    }
    
    class HuggingFaceProvider {
        -api_key: str
        -model: str
        +call_model(prompt, params)
        -handle_api_error(error)
    }
    
    MCPAIIntegration --> AIProvider
    AIProvider <|.. OpenAIProvider
    AIProvider <|.. GoogleProvider
    AIProvider <|.. OllamaProvider
    AIProvider <|.. HuggingFaceProvider
```

## Appium Client Component Detail

```mermaid
classDiagram
    class AppiumClient {
        +session: Session
        +desired_capabilities: Dict
        +appium_server_url: str
        +connect()
        +disconnect()
        +find_element(by, value)
        +find_elements(by, value)
        +get_page_source()
        +get_screenshot()
        +tap(x, y)
        +swipe(start_x, start_y, end_x, end_y)
        +send_keys(element, text)
        +clear(element)
        +press_back()
        +press_home()
        +launch_app(app_id)
        +close_app()
    }
    
    class Session {
        +session_id: str
        +device_info: Dict
        +elements: Dict[str, Element]
        +create_element(element_data)
        +remove_element(element_id)
        +get_element(element_id)
    }
    
    class Element {
        +element_id: str
        +location: Dict
        +size: Dict
        +text: str
        +attributes: Dict
        +tap()
        +send_keys(text)
        +clear()
        +get_attribute(name)
        +is_displayed()
        +is_enabled()
        +is_selected()
    }
    
    AppiumClient --> Session
    Session --> Element
```

## Browser Client Component Detail

```mermaid
classDiagram
    class BrowserClient {
        +playwright: Playwright
        +browser: Browser
        +context: BrowserContext
        +page: Page
        +connect(browser_name, headless)
        +disconnect()
        +navigate_to(url)
        +get_url()
        +get_title()
        +get_content()
        +get_screenshot()
        +find_element(selector)
        +find_elements(selector)
        +click_element(element)
        +send_keys(element, text)
        +execute_script(script, args)
        +wait_for_element(selector, timeout)
    }
    
    class Page {
        +page_id: str
        +goto(url)
        +get_url()
        +get_title()
        +get_content()
        +get_screenshot()
        +find_element(selector)
        +find_elements(selector)
        +evaluate(script, args)
        +wait_for_selector(selector, timeout)
    }
    
    class Element {
        +element_id: str
        +click()
        +type(text)
        +clear()
        +get_attribute(name)
        +inner_text()
        +inner_html()
        +is_visible()
        +is_enabled()
    }
    
    BrowserClient --> Page
    Page --> Element
```

## API Client Component Detail

```mermaid
classDiagram
    class APIClient {
        +base_url: str
        +headers: Dict
        +session: Session
        +timeout: int
        +connect(base_url, headers)
        +disconnect()
        +get(endpoint, params)
        +post(endpoint, data)
        +put(endpoint, data)
        +delete(endpoint)
        +patch(endpoint, data)
        +handle_response(response)
    }
    
    class OpenAPIParser {
        +spec_file: str
        +spec_data: Dict
        +parse_specification()
        +get_endpoints()
        +get_schemas()
        +get_endpoint_parameters(endpoint)
        +get_endpoint_responses(endpoint)
        +generate_example_request(endpoint)
        +validate_request(endpoint, request)
        +validate_response(endpoint, response)
    }
    
    class RobotAPIGenerator {
        +openapi_parser: OpenAPIParser
        +output_file: str
        +generate_robot_suite()
        +generate_settings_section()
        +generate_variables_section()
        +generate_keywords_section()
        +generate_test_cases_section()
        +write_to_file()
    }
    
    APIClient <-- OpenAPIParser
    OpenAPIParser --> RobotAPIGenerator
```

## Robot Test Generation Components

```mermaid
classDiagram
    class RobotGenerator {
        <<interface>>
        +output_file: str
        +generate_robot_suite()
        +generate_settings_section()
        +generate_variables_section()
        +generate_keywords_section()
        +generate_test_cases_section()
        +write_to_file()
    }
    
    class RobotWebGenerator {
        +url: str
        +browser: str
        +selectors: Dict
        +timeout: int
        +generate_robot_suite()
        +generate_settings_section()
        +generate_variables_section()
        +generate_keywords_section()
        +generate_test_cases_section()
        +write_to_file()
    }
    
    class RobotMobileGenerator {
        +app_path: str
        +platform: str
        +selectors: Dict
        +timeout: int
        +generate_robot_suite()
        +generate_settings_section()
        +generate_variables_section()
        +generate_keywords_section()
        +generate_test_cases_section()
        +write_to_file()
    }
    
    class RobotAPIGenerator {
        +openapi_parser: OpenAPIParser
        +base_url: str
        +endpoints: List
        +generate_robot_suite()
        +generate_settings_section()
        +generate_variables_section()
        +generate_keywords_section()
        +generate_test_cases_section()
        +write_to_file()
    }
    
    RobotGenerator <|.. RobotWebGenerator
    RobotGenerator <|.. RobotMobileGenerator
    RobotGenerator <|.. RobotAPIGenerator
```

## Command-Line Interface Flow

```mermaid
flowchart LR
    subgraph CLI[Command-Line Interface]
        ARGS[Parse Arguments] --> TYPE
        TYPE{Test Type} --> WEB[Web Testing]
        TYPE --> MOBILE[Mobile Testing]
        TYPE --> API[API Testing]
        
        WEB --> WCONF[Configure Web Testing]
        MOBILE --> MCONF[Configure Mobile Testing]
        API --> ACONF[Configure API Testing]
        
        WCONF --> GEN[Generate Tests]
        MCONF --> GEN
        ACONF --> GEN
        
        GEN --> OUT[Output Robot File]
    end
```

## File Structure and Organization

```mermaid
graph TB
    ROOT[Project Root] --> MCP[mcp_appium]
    ROOT --> EXAMPLES[examples]
    ROOT --> DOCS[docs]
    ROOT --> SCRIPTS[scripts]
    ROOT --> TESTS[tests]
    ROOT --> DATA[data]
    ROOT --> APP[app]
    
    MCP --> CORE[Core Modules]
    MCP --> API[API Module]
    MCP --> BROWSER[Browser Module]
    MCP --> MOBILE[Mobile Module]
    
    CORE --> INIT[__init__.py]
    CORE --> CLIENT[client.py]
    CORE --> CONFIG[config.py]
    CORE --> AI[ai_integration.py]
    CORE --> SERVER[server.py]
    CORE --> COMMANDS[commands.py]
    CORE --> ELEMENT[element.py]
    CORE --> UTILS[utils.py]
    
    API --> API_CLIENT[api_client.py]
    API --> API_PARSER[openapi_parser.py]
    API --> API_GEN[robot_generator.py]
    API --> API_RUNNER[api_test_runner.py]
    
    BROWSER --> BROWSER_CLIENT[browser.py]
    BROWSER --> BROWSER_PAGE[page.py]
    BROWSER --> BROWSER_ELEMENT[element.py]
    BROWSER --> BROWSER_CONTEXT[context.py]
    
    MOBILE --> MOBILE_CLIENT[mobile_client.py]
    MOBILE --> MOBILE_SESSION[session.py]
    MOBILE --> MOBILE_ELEMENT[element.py]
    
    EXAMPLES --> EX_ANDROID[android_example.py]
    EXAMPLES --> EX_WEB[web_browser_example.py]
    EXAMPLES --> EX_API[api_testing_example.py]
    EXAMPLES --> EX_ROBOT[generate_robot_tests.py]
    EXAMPLES --> EX_ROBOT_WEB[robot_web_generator.py]
    EXAMPLES --> EX_ROBOT_MOB[robot_mobile_generator.py]
    
    SCRIPTS --> SH_ANDROID[run_android_example.sh]
    SCRIPTS --> SH_WEB[run_browser_example.sh]
    SCRIPTS --> SH_API[run_api_example.sh]
    
    DOCS --> DOC_ARCH[ARCHITECTURE.md]
    DOCS --> DOC_BROWSER[BROWSER_AUTOMATION.md]
    DOCS --> DOC_USAGE[USAGE.md]
    DOCS --> DOC_DIAGRAMS[diagrams]
    
    DATA --> DATA_API[api_specs]
    DATA --> DATA_TESTS[generated_tests]
    DATA --> DATA_LOGS[logs]
    DATA --> DATA_SCREENSHOTS[screenshots]
```
