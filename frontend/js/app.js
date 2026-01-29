const API_BASE = '/api/v1';

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupLogout();
    fetchUpdates();
    setupForm();
    setupContractForm();
    setupTabs();
    setupDocTypeSelector();
});

function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
    }
}

function setupLogout() {
    const btn = document.getElementById('logoutBtn');
    btn.addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    });
}


function setupDocTypeSelector() {
    const selector = document.getElementById('docTypeSelector');
    const complaintForm = document.getElementById('complaintForm');
    const contractForm = document.getElementById('contractForm');

    selector.addEventListener('change', (e) => {
        if (e.target.value === 'complaint') {
            complaintForm.classList.remove('hidden');
            contractForm.classList.add('hidden');
        } else {
            complaintForm.classList.add('hidden');
            contractForm.classList.remove('hidden');
        }
    });
}

// --- Tabs ---
function setupTabs() {
    const tabs = document.querySelectorAll('.nav-btn');
    const sections = {
        'generator': document.getElementById('generatorSection'),
        'history': document.getElementById('historySection')
    };

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all
            tabs.forEach(t => t.classList.remove('active'));
            // Add to clicked
            tab.classList.add('active');
            
            // Hide all sections
            Object.values(sections).forEach(sec => sec.classList.add('hidden'));
            
            // Show target
            const target = tab.dataset.tab;
            sections[target].classList.remove('hidden');
            
            if (target === 'history') {
                fetchHistory();
            }
        });
    });
}

// --- History ---
async function fetchHistory() {
    const list = document.getElementById('historyList');
    list.innerHTML = '<p class="text-muted">Kraunama...</p>';
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/documents?limit=20`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = 'login.html';
            return;
        }
        const docs = await response.json();
        
        list.innerHTML = ''; // Clear
        
        if (docs.length === 0) {
            list.innerHTML = '<p class="text-muted">Istorija tuščia. Sugeneruokite pirmą dokumentą!</p>';
            return;
        }
        
        docs.forEach(doc => {
            const date = new Date(doc.created_at).toLocaleString('lt-LT');
            const item = document.createElement('div');
            item.className = 'history-item';
            item.innerHTML = `
                <div class="history-header">
                    <span class="history-title">
                        <span class="badge">${doc.doc_type}</span>${doc.title}
                    </span>
                    <span class="history-date">${date}</span>
                </div>
            `;
            
            // View details on click
            item.addEventListener('click', () => {
                viewDocument(doc);
            });
            
            list.appendChild(item);
        });
        
    } catch (error) {
        console.error('History error:', error);
        list.innerHTML = '<p style="color:red">Nepavyko gauti istorijos.</p>';
    }
}

function viewDocument(doc) {
    // Switch to generator tab (or just reuse result area)
    // For now, let's just show it in the generator result area for simplicity
    const resultArea = document.getElementById('resultArea');
    const resultContent = document.getElementById('resultContent');
    const generatorTab = document.querySelector('[data-tab="generator"]');
    
    // Switch tab
    generatorTab.click();
    
    // content
    resultContent.textContent = doc.content;
    resultArea.style.display = 'block';
    
    // Add a note
    let note = resultArea.querySelector('h3');
    note.textContent = `📄 Peržiūra: ${doc.title}`;
    
    resultArea.scrollIntoView({ behavior: 'smooth' });
}

// --- Updates (Existing) ---
async function fetchUpdates() {
    const list = document.getElementById('updatesList');
    
    try {
        const response = await fetch(`${API_BASE}/legislation/updates?keyword=Darbo%20kodeksas&days=30`);
        const data = await response.json();
        
        list.innerHTML = ''; 
        
        if (data.updates && data.updates.length > 0) {
            data.updates.forEach(update => {
                const li = document.createElement('li');
                li.className = 'update-item';
                li.innerHTML = `
                    <div class="update-date">${update.reg_date}</div>
                    <a href="${update.url}" target="_blank" class="update-title">${update.title}</a>
                `;
                list.appendChild(li);
            });
        } else {
            list.innerHTML = '<li class="update-item text-muted">Naujų pakeitimų nerasta.</li>';
        }
    } catch (error) {
        console.error('Error fetching updates:', error);
        list.innerHTML = '<li class="update-item" style="color: var(--error-color)">Nepavyko užkrauti naujienų.</li>';
    }
}

// --- Form (Existing) ---
function setupForm() {
    const form = document.getElementById('complaintForm');
    const resultArea = document.getElementById('resultArea');
    const resultContent = document.getElementById('resultContent');
    const submitBtn = document.getElementById('submitBtnComplaint'); // ID Changed in HTML
    const btnText = submitBtn.querySelector('span');
    const loader = submitBtn.querySelector('.loader');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        handleSubmission(form, submitBtn, btnText, loader, '/generate/complaint', {
            employee_name: document.getElementById('employeeName').value,
            employer_name: document.getElementById('employerName').value,
            workplace: document.getElementById('workplace').value,
            violation_date: document.getElementById('violationDate').value,
            violation_description: document.getElementById('violationDescription').value
        });
    });
}

function setupContractForm() {
    const form = document.getElementById('contractForm');
    const submitBtn = document.getElementById('submitBtnContract');
    const btnText = submitBtn.querySelector('span');
    const loader = submitBtn.querySelector('.loader');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        handleSubmission(form, submitBtn, btnText, loader, '/generate/contract', {
            employee_name: document.getElementById('c_employeeName').value,
            employer_name: document.getElementById('c_employerName').value,
            position: document.getElementById('c_position').value,
            salary: parseFloat(document.getElementById('c_salary').value),
            workplace: document.getElementById('c_workplace').value,
            start_date: document.getElementById('c_startDate').value,
            additional_conditions: document.getElementById('c_conditions').value
        });
    });
}

async function handleSubmission(form, btn, btnText, loader, endpoint, data) {
    const resultArea = document.getElementById('resultArea');
    const resultContent = document.getElementById('resultContent');

    btn.disabled = true;
    const originalText = btnText.textContent;
    btnText.textContent = 'Generuojama...';
    loader.classList.remove('hidden');
    resultArea.style.display = 'none';

    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });
        
        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = 'login.html';
            return;
        }
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Generavimo klaida');
        }
        
        const responseData = await response.json();
        
        resultContent.textContent = responseData.content;
        resultArea.style.display = 'block';
        resultArea.querySelector('h3').textContent = '📄 Sugeneruotas Dokumentas:';
        resultArea.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        alert(`Klaida: ${error.message}`);
    } finally {
        btn.disabled = false;
        btnText.textContent = originalText;
        loader.classList.add('hidden');
    }
}
