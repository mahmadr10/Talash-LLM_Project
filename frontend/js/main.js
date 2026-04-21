document.addEventListener('DOMContentLoaded', () => {
    const page = window.location.pathname.split('/').pop();

    bindLogin();
    bindUpload('cv-upload-input');
    bindUpload('cv-upload-main');

    if (page === 'index.html' || page === '') {
        loadDashboardData();
    }
    if (page === 'candidates.html') {
        loadCandidatesData();
    }
});

async function apiGet(url) {
    const response = await fetch(url);
    return parseApiResponse(response);
}

async function parseApiResponse(response) {
    const contentType = response.headers.get('content-type') || '';

    if (contentType.includes('application/json')) {
        const payload = await response.json();
        if (!response.ok) {
            throw new Error(payload.error || `Request failed: ${response.status}`);
        }
        return payload;
    }

    const text = await response.text();
    if (text.toLowerCase().includes('the page could not be found')) {
        throw new Error('Backend API is not available on this deployment. Run the Flask backend to use upload and analysis APIs.');
    }

    const snippet = text.replace(/\s+/g, ' ').slice(0, 120);
    throw new Error(`Unexpected API response (${response.status}): ${snippet}`);
}

function bindLogin() {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) return;

    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        window.location.href = 'index.html';
    });
}

function bindUpload(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;

    input.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            const payload = await parseApiResponse(response);

            alert(`CV uploaded successfully for candidate ID ${payload.candidate_id}.`);
            if (window.location.pathname.endsWith('index.html')) {
                loadDashboardData();
            }
            if (window.location.pathname.endsWith('candidates.html')) {
                loadCandidatesData();
            }
        } catch (error) {
            alert(`Upload failed: ${error.message}`);
        } finally {
            input.value = '';
        }
    });
}

async function loadDashboardData() {
    try {
        const [stats, candidates] = await Promise.all([
            apiGet('/api/dashboard-stats'),
            apiGet('/api/candidates')
        ]);

        const statNumbers = document.querySelectorAll('.stat-number');
        if (statNumbers.length >= 3) {
            statNumbers[0].innerHTML = `${stats.total_candidates} <span class="increase">LIVE</span>`;
            statNumbers[1].innerHTML = `${stats.analysis_complete} <span class="percentage">${stats.completion_rate}</span>`;
            statNumbers[2].innerHTML = `${stats.flagged} <span class="action-required">[ACTION REQUIRED]</span>`;
        }

        const tableBody = document.querySelector('.analysis-queue table tbody');
        if (tableBody) {
            tableBody.innerHTML = '';
            candidates.candidates.slice(0, 5).forEach((candidate) => {
                const initials = candidate.name
                    .split(' ')
                    .map(part => part[0])
                    .join('')
                    .slice(0, 2)
                    .toUpperCase();

                const statusClass = candidate.status === 'COMPLETE' ? 'complete' : 'pending';
                const score = candidate.status === 'COMPLETE' ? '90/100' : '--/100';
                tableBody.insertAdjacentHTML('beforeend', `
                    <tr>
                        <td><strong>${initials}</strong> ${candidate.name}<br><small>${candidate.email}</small></td>
                        <td>${new Date().toISOString().slice(0, 10)}</td>
                        <td><span class="status ${statusClass}">${candidate.status}</span></td>
                        <td>${score}</td>
                        <td><a href="analysis.html?id=${candidate.id}">View Analysis</a></td>
                    </tr>
                `);
            });
        }
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
    }
}

async function loadCandidatesData() {
    try {
        const payload = await apiGet('/api/candidates');
        const tableBody = document.querySelector('table tbody');
        if (!tableBody) return;

        tableBody.innerHTML = '';
        payload.candidates.forEach((candidate) => {
            const initials = candidate.name
                .split(' ')
                .map(part => part[0])
                .join('')
                .slice(0, 2)
                .toUpperCase();

            const statusClass = candidate.status === 'COMPLETE' ? 'complete' : 'pending';
            const score = candidate.status === 'COMPLETE' ? '90/100' : '--/100';

            tableBody.insertAdjacentHTML('beforeend', `
                <tr>
                    <td><a href="profile.html?id=${candidate.id}"><strong>${initials}</strong> ${candidate.name}</a><br><small>${candidate.email}</small></td>
                    <td>${new Date().toISOString().slice(0, 10)}</td>
                    <td><span class="status ${statusClass}">${candidate.status}</span></td>
                    <td>${score}</td>
                    <td><a href="analysis.html?id=${candidate.id}" title="View Analysis">View Analysis</a></td>
                </tr>
            `);
        });

        const pageInfo = document.querySelector('.pagination span');
        if (pageInfo) {
            pageInfo.textContent = `DISPLAYING ${payload.candidates.length} OF ${payload.total} CANDIDATE RECORDS`;
        }
    } catch (error) {
        console.error('Failed to load candidates data:', error);
    }
}
