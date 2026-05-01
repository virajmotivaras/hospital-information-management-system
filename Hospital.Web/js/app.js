const http = window.hospitalHttp;
const state = {
  queue: [],
  selectedVisit: null,
  session: null,
};

const titles = {
  desk: ["Patient Desk", "Fast check-in for new and repeat patients."],
  patients: ["Patients", "Search and review registered patients."],
  appointments: ["Appointments", "Schedule gynecology and pediatric visits."],
  prescription: ["Prescription", "Write and print patient prescriptions."],
};

function setStatus(message, isError = false) {
  const el = document.getElementById("save-status");
  el.textContent = message;
  el.classList.toggle("error", isError);
}

async function loadSession() {
  state.session = await http.request("/api/session/");
  const hospital = state.session.hospital;
  document.title = hospital.name;
  document.getElementById("brand-name").textContent = hospital.name;
  document.getElementById("brand-tagline").textContent = hospital.tagline;
  document.getElementById("user-pill").textContent = `${state.session.user.username} | ${state.session.user.roles.join(", ")}`;

  const logo = document.getElementById("brand-logo");
  const mark = document.getElementById("brand-mark");
  if (hospital.logo_url) {
    logo.src = hospital.logo_url;
    logo.hidden = false;
    mark.hidden = true;
  } else {
    logo.hidden = true;
    mark.hidden = false;
    mark.textContent = (hospital.name || "H").trim().slice(0, 1).toUpperCase();
  }

  document.querySelectorAll(".nav-item[data-view]").forEach((item) => {
    item.classList.toggle("hidden", !state.session.permissions[item.dataset.view]);
  });
  document.querySelector(".admin-link").classList.toggle("hidden", !state.session.permissions.admin);

  const active = document.querySelector(".nav-item[data-view]:not(.hidden)");
  if (active) switchView(active.dataset.view);
}

function formData(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function patientLine(patient) {
  const hasAge = patient.age_years !== null && patient.age_years !== undefined && patient.age_years !== "";
  const age = hasAge ? `${escapeHtml(patient.age_years)} yrs` : "Age not set";
  const phone = patient.phone_number ? escapeHtml(patient.phone_number) : "No mobile";
  const guardian = patient.guardian_name ? `Guardian: ${escapeHtml(patient.guardian_name)}` : "";
  return `${age} | ${phone}${guardian ? ` | ${guardian}` : ""}`;
}

function renderQueue() {
  const queueList = document.getElementById("queue-list");
  const prescriptionQueue = document.getElementById("prescription-queue");
  const html = state.queue.length
    ? state.queue.map((visit) => `
      <article class="queue-card">
        <div>
          <strong>${escapeHtml(visit.patient.full_name)}</strong>
          <div class="meta">
            <span class="badge">${escapeHtml(visit.visit_type)}</span>
            <span class="badge">${escapeHtml(visit.department)}</span>
            ${patientLine(visit.patient)}
          </div>
          <div class="meta">${visit.reason ? escapeHtml(visit.reason) : "No reason entered"}</div>
        </div>
        <div>
          <button class="ghost" data-action="consult" data-visit-id="${escapeHtml(visit.id)}">Consult</button>
        </div>
      </article>
    `).join("")
    : `<div class="record-row">No patients waiting.</div>`;
  queueList.innerHTML = html;
  prescriptionQueue.innerHTML = html;
}

async function loadQueue() {
  if (!state.session?.permissions?.desk && !state.session?.permissions?.prescription) return;
  const data = await http.request("/api/visits/");
  state.queue = data.visits;
  renderQueue();
}

async function loadPatients(search = "") {
  if (!state.session?.permissions?.patients) return;
  const data = await http.request(`/api/patients/?search=${encodeURIComponent(search)}`);
  document.getElementById("patient-list").innerHTML = data.patients.length
    ? data.patients.map((patient) => `
      <article class="record-row">
        <strong>${escapeHtml(patient.full_name)}</strong>
        <div class="meta">
          <span class="badge">${escapeHtml(patient.department)}</span>
          ${patientLine(patient)}
        </div>
        <div class="meta">${patient.allergies ? `Allergies: ${escapeHtml(patient.allergies)}` : "No allergies recorded"}</div>
      </article>
    `).join("")
    : `<div class="record-row">No patients found.</div>`;
}

async function loadAppointments() {
  if (!state.session?.permissions?.appointments) return;
  const data = await http.request("/api/appointments/");
  document.getElementById("appointment-list").innerHTML = data.appointments.length
    ? data.appointments.map((item) => `
      <article class="record-row">
        <strong>${escapeHtml(item.patient.full_name)}</strong>
        <div class="meta">
          <span class="badge">${escapeHtml(item.department)}</span>
          ${escapeHtml(new Date(item.scheduled_for).toLocaleString())} | ${item.reason ? escapeHtml(item.reason) : "No reason"}
        </div>
      </article>
    `).join("")
    : `<div class="record-row">No upcoming appointments.</div>`;
}

function addMedicineRow(values = {}) {
  const row = document.createElement("div");
  row.className = "medicine-row";
  row.innerHTML = `
    <input name="medicine_name" placeholder="Medicine" value="${escapeHtml(values.medicine_name || "")}">
    <input name="dosage" placeholder="Dosage" value="${escapeHtml(values.dosage || "")}">
    <input name="frequency" placeholder="Frequency" value="${escapeHtml(values.frequency || "")}">
    <input name="duration" placeholder="Duration" value="${escapeHtml(values.duration || "")}">
    <input name="instructions" placeholder="Instructions" value="${escapeHtml(values.instructions || "")}">
  `;
  document.getElementById("medicine-list").appendChild(row);
}

function selectVisit(visitId) {
  const visit = state.queue.find((item) => String(item.id) === String(visitId));
  if (!visit) return;
  state.selectedVisit = visit;
  const form = document.getElementById("prescription-form");
  form.patient_id.value = visit.patient.id;
  form.visit_id.value = visit.id;
  document.getElementById("selected-patient-label").textContent = visit.patient.full_name;
  switchView("prescription");
}

function switchView(viewName) {
  if (!state.session?.permissions?.[viewName]) return;
  document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
  document.getElementById(`view-${viewName}`).classList.add("active");
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.classList.toggle("active", item.dataset.view === viewName);
  });
  document.getElementById("view-title").textContent = titles[viewName][0];
  document.getElementById("view-subtitle").textContent = titles[viewName][1];
}

function bindEvents() {
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });

  document.body.addEventListener("click", (event) => {
    if (event.target.dataset.action === "consult") {
      selectVisit(event.target.dataset.visitId);
    }
  });

  document.getElementById("refresh-queue").addEventListener("click", loadQueue);
  document.getElementById("refresh-appointments").addEventListener("click", loadAppointments);
  document.getElementById("add-medicine").addEventListener("click", () => addMedicineRow());

  document.getElementById("patient-search").addEventListener("input", (event) => {
    loadPatients(event.target.value).catch((error) => setStatus(error.message, true));
  });

  document.getElementById("checkin-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      setStatus("Saving...");
      await http.request("/api/visits/", {
        method: "POST",
        body: JSON.stringify(formData(event.target)),
      });
      event.target.reset();
      await loadQueue();
      await loadPatients();
      setStatus("Checked in");
    } catch (error) {
      setStatus(error.message, true);
    }
  });

  document.getElementById("appointment-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const data = formData(event.target);
      if (data.scheduled_for) {
        data.scheduled_for = new Date(data.scheduled_for).toISOString();
      }
      await http.request("/api/appointments/", {
        method: "POST",
        body: JSON.stringify(data),
      });
      event.target.reset();
      await loadAppointments();
      setStatus("Appointment saved");
    } catch (error) {
      setStatus(error.message, true);
    }
  });

  document.getElementById("prescription-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const data = formData(event.target);
      data.patient_id = Number(data.patient_id);
      data.visit_id = data.visit_id ? Number(data.visit_id) : null;
      data.items = [...document.querySelectorAll(".medicine-row")].map((row) => ({
        medicine_name: row.querySelector("[name=medicine_name]").value,
        dosage: row.querySelector("[name=dosage]").value,
        frequency: row.querySelector("[name=frequency]").value,
        duration: row.querySelector("[name=duration]").value,
        instructions: row.querySelector("[name=instructions]").value,
      }));
      const result = await http.request("/api/prescriptions/", {
        method: "POST",
        body: JSON.stringify(data),
      });
      await loadQueue();
      setStatus("Prescription saved");
      window.open(result.print_url, "_blank", "noopener");
    } catch (error) {
      setStatus(error.message, true);
    }
  });
}

async function start() {
  bindEvents();
  await loadSession();
  addMedicineRow({ frequency: "1-0-1" });
  await Promise.all([loadQueue(), loadPatients(), loadAppointments()]);
}

start().catch((error) => setStatus(error.message, true));
