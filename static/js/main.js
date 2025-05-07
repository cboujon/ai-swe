// Global state
let currentMarkdown = '';
let parsedSpec = null;
let diagrams = null;
let selectedUseCaseId = null;
let editor = null; // Toast UI Editor instance

// Sample template to help users get started with a software specification
const TEMPLATE_MARKDOWN = `# My Software Project

## Description
A brief description of your software project.

## Classes

### User
A user of the system.

#### Attributes
- id: int
- username: str
- email: str
- password: str = "" // Hashed password

#### Methods
- authenticate(password: str) -> bool // Authenticate user
- updateProfile(data: Dict) -> bool // Update user profile

### Product
A product in the system.

#### Attributes
- id: int
- name: str
- price: float
- description: str = ""

#### Methods
- getDetails() -> Dict // Get product details
- updatePrice(price: float) -> bool // Update product price

## Architecture

### Frontend
The user interface of the application.

#### Responsibilities
- Render user interface
- Handle user inputs
- Communicate with backend

#### Interactions
- Backend -> Send user requests

### Backend
The server-side of the application.

#### Responsibilities
- Process requests
- Business logic
- Data storage

#### Interactions
- Database -> Store and retrieve data

### Database
The data persistence layer.

#### Responsibilities
- Store data
- Provide data access
- Ensure data integrity

## Use Cases

### Register User
Allow a new user to register in the system.

#### Actors
- Visitor

#### Preconditions
- User is not logged in

#### Flow
1. Visitor -> System: Access registration form
2. Visitor -> System: Fill in user details
3. System -> Database: Save user data
4. System -> User: Confirm registration

#### Postconditions
- New user account is created
- User is logged in

### Purchase Product
Allow a user to purchase a product.

#### Actors
- User

#### Preconditions
- User is logged in
- Product is available

#### Flow
1. User -> System: Select product
2. User -> System: Add to cart
3. User -> System: Proceed to checkout
4. System -> Payment Gateway: Process payment
5. System -> Database: Update inventory
6. System -> User: Confirm purchase

#### Postconditions
- Purchase is recorded
- Inventory is updated
- User receives confirmation
`;

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Toast UI Editor
    initEditor();
    
    // Initialize navigation
    initNavigation();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize Mermaid
    initMermaid();
    
    // Show the Software Spec page by default
    showPage('software-spec');
});

// Initialize Toast UI Editor
function initEditor() {
    const editorElement = document.getElementById('markdown-editor');
    if (!editorElement) return;
    
    // Initialize the editor with options
    editor = new toastui.Editor({
        el: editorElement,
        height: '500px',
        initialEditType: 'markdown',
        previewStyle: 'vertical',
        initialValue: TEMPLATE_MARKDOWN,
        toolbarItems: [
            ['heading', 'bold', 'italic', 'strike'],
            ['hr', 'quote'],
            ['ul', 'ol', 'task', 'indent', 'outdent'],
            ['table', 'image', 'link'],
            ['code', 'codeblock'],
            ['scrollSync']
        ],
        // Add responsive handling
        events: {
            load: function() {
                // Set the width of editor container to its parent width
                const editorContainer = document.querySelector('.toastui-editor-defaultUI');
                if (editorContainer) {
                    editorContainer.style.width = '100%';
                }
                
                // Adjust internal components
                const mdPreview = document.querySelector('.toastui-editor-md-preview');
                if (mdPreview) {
                    mdPreview.style.maxWidth = '100%';
                }
            }
        }
    });
    
    // Add window resize handler
    window.addEventListener('resize', () => {
        adjustEditorSize();
    });
    
    // Initial adjustment
    adjustEditorSize();
    
    // Sync the editor content with the hidden textarea
    editor.on('change', () => {
        const markdownContent = editor.getMarkdown();
        const markdownInput = document.getElementById('markdown-input');
        if (markdownInput) {
            markdownInput.value = markdownContent;
        }
        currentMarkdown = markdownContent;
    });
    
    // Trigger initial sync
    const markdownInput = document.getElementById('markdown-input');
    if (markdownInput) {
        markdownInput.value = editor.getMarkdown();
        currentMarkdown = editor.getMarkdown();
    }
}

// Adjust editor size on window resize
function adjustEditorSize() {
    if (!editor) return;
    
    // Get the parent container width
    const editorContainer = document.querySelector('.markdown-editor');
    if (!editorContainer) return;
    
    // Force editor UI to redraw
    const editorUI = document.querySelector('.toastui-editor-defaultUI');
    if (editorUI) {
        editorUI.style.width = '100%';
        editorUI.style.maxWidth = '100%';
    }
    
    // Force markdown side and preview side to be capped at 50% on vertical layout
    const mdContainer = document.querySelector('.toastui-editor-md-container');
    const previewContainer = document.querySelector('.toastui-editor-md-preview');
    
    if (mdContainer && previewContainer && window.innerWidth > 768) {
        mdContainer.style.maxWidth = '50%';
        previewContainer.style.maxWidth = '50%';
    }
}

// Initialize navigation functionality
function initNavigation() {
    const navLinks = document.querySelectorAll('.sidebar-menu a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the target page ID from the href attribute
            const targetId = this.getAttribute('href').substring(1);
            
            // Show the corresponding page
            showPage(targetId);
            
            // Highlight the active nav link
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Mark the first link as active by default
    if (navLinks.length > 0) {
        navLinks[0].classList.add('active');
    }
}

// Show a specific page and hide others
function showPage(pageId) {
    const pages = document.querySelectorAll('.page');
    
    pages.forEach(page => {
        if (page.id === pageId) {
            page.classList.add('active');
            
            // Special handling for specific pages
            if (pageId === 'class-diagram') {
                renderClassDiagram();
            } else if (pageId === 'architecture-diagram') {
                renderArchitectureDiagram();
            } else if (pageId === 'use-cases') {
                loadUseCases();
            } else if (pageId === 'code-view') {
                generateCode();
            } else if (pageId === 'software-spec' && editor) {
                // Update editor when returning to spec page
                editor.focus();
            }
        } else {
            page.classList.remove('active');
        }
    });
}

// Set up event listeners for buttons and inputs
function setupEventListeners() {
    // Process button in the Software Spec page
    const processButton = document.getElementById('process-button');
    if (processButton) {
        processButton.addEventListener('click', processMarkdown);
    }
    
    // Use case selector dropdown
    const useCaseSelect = document.getElementById('use-case-select');
    if (useCaseSelect) {
        useCaseSelect.addEventListener('change', function() {
            const selectedId = this.value;
            if (selectedId) {
                selectedUseCaseId = selectedId;
                displaySelectedUseCase();
            }
        });
    }
    
    // Generate code button
    const generateCodeButton = document.getElementById('generate-code-button');
    if (generateCodeButton) {
        generateCodeButton.addEventListener('click', generateCode);
    }
}

// Initialize Mermaid
function initMermaid() {
    mermaid.initialize({
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
        flowchart: { useMaxWidth: true },
        sequence: { useMaxWidth: true }
    });
}

// Process the markdown input
async function processMarkdown() {
    // Get the latest markdown content from the editor
    if (editor) {
        currentMarkdown = editor.getMarkdown();
    } else {
        const markdownInput = document.getElementById('markdown-input');
        if (!markdownInput || !markdownInput.value.trim()) {
            showError('Please enter a software specification in Markdown format.');
            return;
        }
        currentMarkdown = markdownInput.value;
    }
    
    if (!currentMarkdown.trim()) {
        showError('Please enter a software specification in Markdown format.');
        return;
    }
    
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    
    try {
        // Show loading spinner
        if (loadingSpinner) loadingSpinner.style.display = 'block';
        if (errorMessage) errorMessage.style.display = 'none';
        
        // Send markdown to the server for processing
        const response = await fetch('/api/generate-diagrams', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ markdown: currentMarkdown })
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        
        // Parse the response
        const data = await response.json();
        
        // Store the diagrams and parsed spec
        diagrams = data;
        parsedSpec = data.parsed_spec;
        
        // Update the preview with success message
        const previewElement = document.getElementById('markdown-preview');
        if (previewElement) {
            previewElement.innerHTML = '<div class="alert alert-success">Software specification processed successfully!</div>';
        }
        
        // Enable navigation to diagram pages
        enableNavigation();
        
        // Hide loading spinner
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        
    } catch (error) {
        console.error('Error processing markdown:', error);
        showError(`Error processing the specification: ${error.message}`);
        
        // Hide loading spinner
        if (loadingSpinner) loadingSpinner.style.display = 'none';
    }
}

// Enable navigation to all pages after processing is complete
function enableNavigation() {
    const navLinks = document.querySelectorAll('.sidebar-menu a');
    navLinks.forEach(link => {
        link.classList.remove('disabled');
    });
}

// Show error message
function showError(message) {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
    
    const loadingSpinner = document.getElementById('loading-spinner');
    if (loadingSpinner) {
        loadingSpinner.style.display = 'none';
    }
}

// Render the class diagram
function renderClassDiagram() {
    const diagramContainer = document.getElementById('class-diagram-container');
    if (!diagramContainer) return;
    
    if (!diagrams || !diagrams.class) {
        diagramContainer.innerHTML = '<div class="alert alert-warning">No class diagram data available. Please process a specification first.</div>';
        return;
    }
    
    // Display the Mermaid code
    const codeElement = document.getElementById('class-diagram-code');
    if (codeElement) {
        codeElement.textContent = diagrams.class;
    }
    
    // Render the diagram
    diagramContainer.innerHTML = '<div class="mermaid">' + diagrams.class + '</div>';
    mermaid.init(undefined, diagramContainer.querySelectorAll('.mermaid'));
}

// Render the architecture diagram
function renderArchitectureDiagram() {
    const diagramContainer = document.getElementById('architecture-diagram-container');
    if (!diagramContainer) return;
    
    if (!diagrams || !diagrams.architecture) {
        diagramContainer.innerHTML = '<div class="alert alert-warning">No architecture diagram data available. Please process a specification first.</div>';
        return;
    }
    
    // Display the Mermaid code
    const codeElement = document.getElementById('architecture-diagram-code');
    if (codeElement) {
        codeElement.textContent = diagrams.architecture;
    }
    
    // Render the diagram
    diagramContainer.innerHTML = '<div class="mermaid">' + diagrams.architecture + '</div>';
    mermaid.init(undefined, diagramContainer.querySelectorAll('.mermaid'));
}

// Load use cases into the dropdown
function loadUseCases() {
    const useCaseSelect = document.getElementById('use-case-select');
    if (!useCaseSelect) return;
    
    // Clear the dropdown
    useCaseSelect.innerHTML = '<option value="">Select a use case</option>';
    
    if (!parsedSpec || !parsedSpec.use_cases || parsedSpec.use_cases.length === 0) {
        const useCaseContainer = document.getElementById('use-case-content');
        if (useCaseContainer) {
            useCaseContainer.innerHTML = '<div class="alert alert-warning">No use cases available. Please process a specification first.</div>';
        }
        return;
    }
    
    // Populate the dropdown with use cases
    parsedSpec.use_cases.forEach(useCase => {
        const option = document.createElement('option');
        option.value = useCase.id;
        option.textContent = `${useCase.id}: ${useCase.name}`;
        useCaseSelect.appendChild(option);
    });
    
    // If there's at least one use case, select it by default
    if (parsedSpec.use_cases.length > 0) {
        selectedUseCaseId = parsedSpec.use_cases[0].id;
        useCaseSelect.value = selectedUseCaseId;
        displaySelectedUseCase();
    }
}

// Display the selected use case
async function displaySelectedUseCase() {
    const useCaseContainer = document.getElementById('use-case-content');
    const useCaseDiagramContainer = document.getElementById('use-case-diagram-container');
    
    if (!useCaseContainer || !useCaseDiagramContainer) return;
    
    if (!selectedUseCaseId || !parsedSpec || !parsedSpec.use_cases) {
        useCaseContainer.innerHTML = '<div class="alert alert-warning">No use case selected.</div>';
        useCaseDiagramContainer.innerHTML = '';
        return;
    }
    
    // Find the selected use case
    const useCase = parsedSpec.use_cases.find(uc => uc.id === selectedUseCaseId);
    if (!useCase) {
        useCaseContainer.innerHTML = '<div class="alert alert-warning">Selected use case not found.</div>';
        useCaseDiagramContainer.innerHTML = '';
        return;
    }
    
    // Display use case details
    useCaseContainer.innerHTML = `
        <h3>${useCase.name}</h3>
        <div class="use-case-description">
            <p>${useCase.description}</p>
            
            <h4>Actors</h4>
            <ul>
                ${useCase.actors.map(actor => `<li>${actor}</li>`).join('')}
            </ul>
            
            <h4>Preconditions</h4>
            <ul>
                ${useCase.preconditions.map(pre => `<li>${pre}</li>`).join('')}
            </ul>
            
            <h4>Flow</h4>
            <ol>
                ${useCase.flow.map(step => `<li>${step.actor} -> ${step.action}${step.message ? ': ' + step.message : ''}</li>`).join('')}
            </ol>
            
            <h4>Postconditions</h4>
            <ul>
                ${useCase.postconditions.map(post => `<li>${post}</li>`).join('')}
            </ul>
        </div>
    `;
    
    // Generate and display the sequence diagram
    try {
        // Show loading indicator
        useCaseDiagramContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';
        
        // Request sequence diagram for this use case
        const response = await fetch('/api/generate-sequence-diagram', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                use_case_id: selectedUseCaseId,
                use_case_data: useCase,
                parsed_spec: parsedSpec,
                markdown: currentMarkdown
            })
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.mermaid) {
            // Display the Mermaid code
            const codeElement = document.getElementById('sequence-diagram-code');
            if (codeElement) {
                codeElement.textContent = data.mermaid;
            }
            
            // Render the diagram
            useCaseDiagramContainer.innerHTML = '<div class="mermaid">' + data.mermaid + '</div>';
            mermaid.init(undefined, useCaseDiagramContainer.querySelectorAll('.mermaid'));
        } else {
            useCaseDiagramContainer.innerHTML = '<div class="alert alert-warning">Failed to generate sequence diagram.</div>';
        }
        
    } catch (error) {
        console.error('Error generating sequence diagram:', error);
        useCaseDiagramContainer.innerHTML = `<div class="alert alert-danger">Error generating sequence diagram: ${error.message}</div>`;
    }
}

// Generate code from the parsed specification
async function generateCode() {
    const codeContainer = document.getElementById('code-container');
    
    if (!codeContainer) return;
    
    if (!parsedSpec || !diagrams) {
        codeContainer.innerHTML = '<div class="alert alert-warning">No specification data available. Please process a specification first.</div>';
        return;
    }
    
    try {
        // Show loading indicator
        codeContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';
        
        // Request code generation
        const response = await fetch('/api/generate-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                parsed_spec: parsedSpec,
                diagrams: diagrams
            })
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Display the generated code
        let codeHtml = '<div class="code-files">';
        
        Object.entries(data).forEach(([filename, content]) => {
            codeHtml += `
                <div class="code-file">
                    <div class="code-filename">${filename}</div>
                    <pre><code class="language-python">${escapeHtml(content)}</code></pre>
                </div>
            `;
        });
        
        codeHtml += '</div>';
        codeContainer.innerHTML = codeHtml;
        
        // Highlight code if highlightjs is available
        if (typeof hljs !== 'undefined') {
            document.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightBlock(block);
            });
        }
        
    } catch (error) {
        console.error('Error generating code:', error);
        codeContainer.innerHTML = `<div class="alert alert-danger">Error generating code: ${error.message}</div>`;
    }
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
} 