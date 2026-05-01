const http = window.hospitalHttp;
const state = {
  queue: [],
  selectedVisit: null,
  selectedPatientId: null,
  session: null,
  calendarWeekStart: null,
  calendarAppointments: [],
};

const titles = {
  calendar: ["Calendar", "Weekly appointment view."],
  desk: ["Patient Desk", "Fast check-in for new and repeat patients."],
  patients: ["Patients", "Search and review registered patients."],
  appointments: ["Appointments", "Schedule patient visits."],
  prescription: ["Prescription", "Write and print patient prescriptions."],
};

const symptomSuggestions = [
  "Abdominal bloating",
  "Abdominal cramps",
  "Abdominal distension",
  "Abdominal pain",
  "Acid reflux",
  "Acne",
  "Ankle swelling",
  "Anxiety",
  "Appetite loss",
  "Back pain",
  "Bad breath",
  "Bleeding after intercourse",
  "Bleeding gums",
  "Blurred vision",
  "Body ache",
  "Breast discharge",
  "Breast lump",
  "Breast pain",
  "Breathlessness",
  "Burning micturition",
  "Burning sensation",
  "Calf pain",
  "Chest discomfort",
  "Chest pain",
  "Chills",
  "Constipation",
  "Cough",
  "Crying spells",
  "Decreased fetal movements",
  "Decreased urine output",
  "Delayed periods",
  "Depressed mood",
  "Diarrhea",
  "Difficulty breathing",
  "Difficulty feeding",
  "Difficulty passing stool",
  "Difficulty sleeping",
  "Dizziness",
  "Dry cough",
  "Ear discharge",
  "Ear pain",
  "Excessive thirst",
  "Eye discharge",
  "Facial swelling",
  "Fainting",
  "Fatigue",
  "Fever",
  "Food aversion",
  "Frequent urination",
  "Giddiness",
  "Groin pain",
  "Hair fall",
  "Headache",
  "Heartburn",
  "Heavy menstrual bleeding",
  "High blood pressure",
  "Hoarseness of voice",
  "Hot flashes",
  "Increased appetite",
  "Increased fetal movements",
  "Irregular periods",
  "Itching",
  "Joint pain",
  "Leg cramps",
  "Loose stools",
  "Loss of smell",
  "Loss of taste",
  "Low back pain",
  "Lower abdominal pain",
  "Menstrual cramps",
  "Missed period",
  "Mood changes",
  "Morning sickness",
  "Mouth ulcers",
  "Nasal congestion",
  "Nausea",
  "Neck pain",
  "Nipple pain",
  "Pain during intercourse",
  "Painful periods",
  "Palpitations",
  "Pelvic pain",
  "Poor feeding",
  "Post-delivery bleeding",
  "Rash",
  "Reduced appetite",
  "Seizure",
  "Shortness of breath",
  "Shoulder pain",
  "Skin discoloration",
  "Sore throat",
  "Spotting",
  "Swelling of feet",
  "Swelling of hands",
  "Swollen lymph nodes",
  "Throat pain",
  "Tiredness",
  "Tooth pain",
  "Upper abdominal pain",
  "Urinary frequency",
  "Urinary incontinence",
  "Vaginal bleeding",
  "Vaginal discharge",
  "Vaginal dryness",
  "Vaginal itching",
  "Vaginal pain",
  "Vomiting",
  "Weakness",
  "Weight gain",
  "Weight loss",
  "Wheezing",
  "White discharge",
  "Wound pain",
  "Wound discharge",
  "Yellow discharge",
  "Abnormal uterine bleeding",
  "Amenorrhea",
  "Anemia symptoms",
  "Antenatal vomiting",
  "Breast engorgement",
  "Contractions",
  "Dysmenorrhea",
  "Dyspareunia",
  "Edema in pregnancy",
  "Excessive sweating",
  "Foul smelling discharge",
  "Gestational swelling",
  "Hemorrhoids",
  "Infertility concern",
  "Leaking per vaginum",
  "Menorrhagia",
  "Oligomenorrhea",
  "Pain abdomen in pregnancy",
  "Painful urination",
  "Postpartum fever",
  "Preterm pain",
  "Pruritus",
  "Puerperal bleeding",
  "Secondary amenorrhea",
  "Severe headache in pregnancy",
  "Vaginal spotting",
  "Water breaking",
  "Bedwetting",
  "Colic",
  "Convulsions",
  "Delayed milestones",
  "Excessive crying",
  "Failure to gain weight",
  "Fast breathing",
  "Feeding difficulty",
  "Irritability",
  "Jaundice",
  "Lethargy",
  "Poor weight gain",
  "Runny nose",
  "Skin rash",
  "Vomiting in child",
  "Worms in stool",
  "Blood in stool",
  "Blood in urine",
  "Burning eyes",
  "Cold extremities",
  "Confusion",
  "Dehydration",
  "Excessive sleepiness",
  "Facial pain",
  "Hives",
  "Numbness",
  "Pain at injection site",
  "Red eye",
  "Restlessness",
  "Sneezing",
  "Stomach pain",
  "Swelling",
  "Tingling",
  "Tremors",
  "Urine urgency",
  "Vertigo",
  "Visual disturbance",
  "Yellow eyes",
].sort((a, b) => a.localeCompare(b));

function setStatus(message, isError = false) {
  const el = document.getElementById("save-status");
  el.textContent = message;
  el.classList.toggle("error", isError);
}

function loadSymptomSuggestions() {
  const datalist = document.getElementById("symptom-options");
  datalist.innerHTML = symptomSuggestions
    .map((symptom) => `<option value="${escapeHtml(symptom)}"></option>`)
    .join("");
}

function addDiagnosisSymptom() {
  const input = document.getElementById("diagnosis-symptom-input");
  const textarea = document.querySelector("#prescription-form [name=diagnosis]");
  const symptom = input.value.trim();
  if (!symptom) return;

  const existing = textarea.value.trim();
  const separator = existing ? "; " : "";
  textarea.value = `${existing}${separator}${symptom}`;
  input.value = "";
  textarea.focus();
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
  populateDepartmentSelects();

  const roles = state.session.user.roles || [];
  const preferredView = roles.includes("Doctor") && state.session.permissions.calendar ? "calendar" : "";
  const active = preferredView
    ? document.querySelector(`.nav-item[data-view="${preferredView}"]`)
    : document.querySelector(".nav-item[data-view]:not(.hidden)");
  if (active) switchView(active.dataset.view);
}

function populateDepartmentSelects() {
  const departments = state.session?.departments || [];
  const options = departments.length
    ? departments.map((department) => `<option value="${escapeHtml(department.code)}">${escapeHtml(department.name)}</option>`).join("")
    : `<option value="GENERAL">General</option>`;
  document.querySelectorAll("[data-department-select]").forEach((select) => {
    const current = select.value;
    select.innerHTML = options;
    if (current) select.value = current;
  });
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

function departmentName(code) {
  const department = (state.session?.departments || []).find((item) => item.code === code);
  return department ? department.name : code;
}

function startOfWeek(date) {
  const result = new Date(date);
  result.setHours(0, 0, 0, 0);
  const day = result.getDay();
  const offset = day === 0 ? -6 : 1 - day;
  result.setDate(result.getDate() + offset);
  return result;
}

function addDays(date, days) {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

function formatCalendarDay(date) {
  return date.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
}

function formatCalendarTime(dateString) {
  return new Date(dateString).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

function sameLocalDate(first, second) {
  return first.getFullYear() === second.getFullYear()
    && first.getMonth() === second.getMonth()
    && first.getDate() === second.getDate();
}

function renderCalendar() {
  const weekStart = state.calendarWeekStart || startOfWeek(new Date());
  state.calendarWeekStart = weekStart;
  const weekEnd = addDays(weekStart, 6);
  document.getElementById("calendar-week-label").textContent =
    `${formatCalendarDay(weekStart)} - ${formatCalendarDay(weekEnd)}`;

  const today = new Date();
  const html = Array.from({ length: 7 }, (_item, index) => {
    const day = addDays(weekStart, index);
    const appointments = state.calendarAppointments.filter((appointment) =>
      sameLocalDate(new Date(appointment.scheduled_for), day)
    );
    const items = appointments.length
      ? appointments.map((appointment) => `
        <article class="calendar-appointment">
          <strong>${escapeHtml(formatCalendarTime(appointment.scheduled_for))} ${escapeHtml(appointment.patient.full_name)}</strong>
          <div class="meta">
            <span class="badge">${escapeHtml(departmentName(appointment.department))}</span>
            <span class="badge">${escapeHtml(appointment.status)}</span>
          </div>
          <div class="meta">${appointment.reason ? escapeHtml(appointment.reason) : "No reason entered"}</div>
        </article>
      `).join("")
      : `<div class="calendar-empty">No appointments</div>`;

    return `
      <section class="calendar-day ${sameLocalDate(day, today) ? "today" : ""}">
        <div class="calendar-day-heading">
          <strong>${escapeHtml(day.toLocaleDateString(undefined, { weekday: "long" }))}</strong>
          <span>${escapeHtml(day.toLocaleDateString(undefined, { month: "short", day: "numeric" }))}</span>
        </div>
        <div class="calendar-items">${items}</div>
      </section>
    `;
  }).join("");

  document.getElementById("calendar-week").innerHTML = html;
}

async function loadCalendarAppointments() {
  if (!state.session?.permissions?.calendar) return;
  if (!state.calendarWeekStart) state.calendarWeekStart = startOfWeek(new Date());
  const start = state.calendarWeekStart;
  const end = addDays(start, 7);
  const data = await http.request(`/api/appointments/?start=${encodeURIComponent(start.toISOString())}&end=${encodeURIComponent(end.toISOString())}`);
  state.calendarAppointments = data.appointments;
  renderCalendar();
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
            <span class="badge">${escapeHtml(departmentName(visit.department))}</span>
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
      <article class="record-row clickable" data-action="view-patient" data-patient-id="${escapeHtml(patient.id)}">
        <strong>${escapeHtml(patient.full_name)}</strong>
        <div class="meta">
          <span class="badge">${escapeHtml(departmentName(patient.department))}</span>
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
          <span class="badge">${escapeHtml(departmentName(item.department))}</span>
          ${escapeHtml(new Date(item.scheduled_for).toLocaleString())} | ${item.reason ? escapeHtml(item.reason) : "No reason"}
        </div>
      </article>
    `).join("")
    : `<div class="record-row">No upcoming appointments.</div>`;
}

function renderHistoryList(containerId, items, renderer, emptyText) {
  document.getElementById(containerId).innerHTML = items.length
    ? items.map(renderer).join("")
    : `<div class="mini-card meta">${escapeHtml(emptyText)}</div>`;
}

function appointmentCard(item) {
  return `
    <article class="mini-card">
      <strong>${escapeHtml(new Date(item.scheduled_for).toLocaleString())}</strong>
      <div class="meta">
        <span class="badge">${escapeHtml(item.status)}</span>
        <span class="badge">${escapeHtml(departmentName(item.department))}</span>
      </div>
      <div class="meta">${item.reason ? escapeHtml(item.reason) : "No reason entered"}</div>
    </article>
  `;
}

function prescriptionCard(item) {
  const medicines = item.items.map((medicine) => escapeHtml(medicine.medicine_name)).join(", ");
  return `
    <article class="mini-card">
      <strong>${escapeHtml(new Date(item.created_at).toLocaleString())}</strong>
      <div class="meta">Dr. ${escapeHtml(item.doctor_name)} | ${item.diagnosis ? escapeHtml(item.diagnosis) : "No diagnosis entered"}</div>
      <div class="meta">${medicines || "No medicines listed"}</div>
      <button class="ghost" data-action="print-prescription" data-print-url="${escapeHtml(item.print_url)}" type="button">Print</button>
    </article>
  `;
}

function billCard(item) {
  return `
    <article class="mini-card">
      <strong>Bill #${escapeHtml(item.id)}</strong>
      <div class="meta">
        <span class="badge">${escapeHtml(item.status)}</span>
        ${escapeHtml(new Date(item.created_at).toLocaleString())}
      </div>
      <div class="amount-row"><span>Total</span><span>${escapeHtml(item.total_amount)}</span></div>
      <div class="amount-row"><span>Paid</span><span>${escapeHtml(item.paid_amount)}</span></div>
      <div class="amount-row"><span>Due</span><span>${escapeHtml(item.due_amount)}</span></div>
    </article>
  `;
}

async function openPatientDetail(patientId) {
  state.selectedPatientId = patientId;
  const data = await http.request(`/api/patients/${encodeURIComponent(patientId)}/history/`);
  document.getElementById("patient-detail").classList.remove("hidden");
  document.getElementById("detail-patient-name").textContent = data.patient.full_name;
  document.getElementById("detail-patient-meta").textContent = `${departmentName(data.patient.department)} | ${patientLine(data.patient)}`;
  document.querySelector("#bill-form [name=patient_id]").value = data.patient.id;
  document.getElementById("bill-form").classList.toggle("hidden", !state.session.permissions.billing);

  renderHistoryList("detail-upcoming-appointments", data.appointments.upcoming, appointmentCard, "No upcoming appointments.");
  renderHistoryList("detail-past-appointments", data.appointments.past, appointmentCard, "No past appointments.");
  renderHistoryList(
    "detail-prescriptions",
    data.prescriptions,
    prescriptionCard,
    state.session.permissions.prescription ? "No prescriptions yet." : "Prescription history is available to Doctor and Admin users."
  );
  renderHistoryList(
    "detail-bills",
    data.bills,
    billCard,
    state.session.permissions.billing ? "No bills yet." : "Billing history is available to Reception and Admin users."
  );
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
  if (viewName === "calendar") {
    loadCalendarAppointments().catch((error) => setStatus(error.message, true));
  }
}

function bindEvents() {
  document.querySelectorAll(".nav-item[data-view]").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });

  document.body.addEventListener("click", (event) => {
    if (event.target.dataset.action === "consult") {
      selectVisit(event.target.dataset.visitId);
    }
    if (event.target.closest("[data-action='view-patient']")) {
      const row = event.target.closest("[data-action='view-patient']");
      openPatientDetail(row.dataset.patientId).catch((error) => setStatus(error.message, true));
    }
    if (event.target.dataset.action === "print-prescription") {
      window.open(event.target.dataset.printUrl, "_blank", "noopener");
    }
  });

  document.getElementById("refresh-queue").addEventListener("click", loadQueue);
  document.getElementById("refresh-appointments").addEventListener("click", loadAppointments);
  document.getElementById("previous-week").addEventListener("click", () => {
    state.calendarWeekStart = addDays(state.calendarWeekStart || startOfWeek(new Date()), -7);
    loadCalendarAppointments().catch((error) => setStatus(error.message, true));
  });
  document.getElementById("current-week").addEventListener("click", () => {
    state.calendarWeekStart = startOfWeek(new Date());
    loadCalendarAppointments().catch((error) => setStatus(error.message, true));
  });
  document.getElementById("next-week").addEventListener("click", () => {
    state.calendarWeekStart = addDays(state.calendarWeekStart || startOfWeek(new Date()), 7);
    loadCalendarAppointments().catch((error) => setStatus(error.message, true));
  });
  document.getElementById("close-patient-detail").addEventListener("click", () => {
    document.getElementById("patient-detail").classList.add("hidden");
    state.selectedPatientId = null;
  });
  document.getElementById("add-medicine").addEventListener("click", () => addMedicineRow());
  document.getElementById("add-diagnosis-symptom").addEventListener("click", addDiagnosisSymptom);
  document.getElementById("diagnosis-symptom-input").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      addDiagnosisSymptom();
    }
  });

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
      await loadCalendarAppointments();
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
      if (state.selectedPatientId) await openPatientDetail(state.selectedPatientId);
      setStatus("Prescription saved");
      window.open(result.print_url, "_blank", "noopener");
    } catch (error) {
      setStatus(error.message, true);
    }
  });

  document.getElementById("bill-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const data = formData(event.target);
      await http.request(`/api/patients/${encodeURIComponent(data.patient_id)}/bills/`, {
        method: "POST",
        body: JSON.stringify({
          paid_amount: data.paid_amount,
          notes: data.notes,
          items: [
            {
              description: data.description,
              quantity: data.quantity,
              unit_price: data.unit_price,
            },
          ],
        }),
      });
      event.target.reset();
      event.target.quantity.value = "1";
      await openPatientDetail(data.patient_id);
      setStatus("Bill saved");
    } catch (error) {
      setStatus(error.message, true);
    }
  });
}

async function start() {
  bindEvents();
  loadSymptomSuggestions();
  await loadSession();
  addMedicineRow({ frequency: "1-0-1" });
  await Promise.all([loadQueue(), loadPatients(), loadAppointments(), loadCalendarAppointments()]);
}

start().catch((error) => setStatus(error.message, true));
