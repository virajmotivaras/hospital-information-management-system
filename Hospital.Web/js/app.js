const http = window.hospitalHttp;
const state = {
  queue: [],
  selectedVisit: null,
  selectedPatientId: null,
  session: null,
  calendarWeekStart: null,
  calendarAppointments: [],
  appointmentPatientSuggestions: [],
  patientCache: [],
  appointmentPatientSearchToken: 0,
  calendarRefreshTimer: null,
  calendarRefreshInFlight: false,
  lastPrescriptionPrintUrl: "",
};

const CALENDAR_REFRESH_MS = 8000;

const titles = {
  calendar: ["Calendar", "Weekly appointment view."],
  desk: ["Patient Desk", "Fast check-in for new and repeat patients."],
  patients: ["Patients", "Search and review registered patients."],
  appointments: ["Appointments", "Schedule patient visits."],
  prescription: ["Prescription", "Write and print patient prescriptions."],
};

const commonSymptomSuggestions = [
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

const symptomSuggestions = [
  ...new Set([
    ...(window.icd10SymptomSuggestions || []).map((item) => `${item.code} - ${item.description}`),
    ...commonSymptomSuggestions,
  ]),
].sort((a, b) => a.localeCompare(b));

function setStatus(message, isError = false) {
  const el = document.getElementById("save-status");
  el.textContent = message;
  el.classList.toggle("error", isError);
}

function loadSymptomSuggestions() {
  const datalist = document.getElementById("symptom-options");
  if (!datalist) return;
  datalist.innerHTML = symptomSuggestions
    .map((symptom) => `<option value="${escapeHtml(symptom)}"></option>`)
    .join("");
}

function addSymptom() {
  const input = document.getElementById("symptom-input");
  const daysInput = document.getElementById("symptom-days-input");
  const symptom = input.value.trim();
  if (!symptom) return;

  addSymptomRow({ symptom, days: daysInput.value.trim() });
  input.value = "";
  daysInput.value = "";
  input.focus();
}

function addSymptomRow(values = {}) {
  const symptomList = document.getElementById("symptom-list");
  if (!symptomList) return;
  const row = document.createElement("div");
  row.className = "symptom-row";
  row.innerHTML = `
    <input data-field="symptom" list="symptom-options" value="${escapeHtml(values.symptom || "")}" placeholder="Symptom">
    <input data-field="days" type="number" min="0" max="3650" value="${escapeHtml(values.days ?? "")}" placeholder="Days">
    <button class="ghost" data-action="remove-symptom" type="button">Remove</button>
  `;
  symptomList.appendChild(row);
}

function symptomEntries() {
  return [...document.querySelectorAll(".symptom-row")]
    .map((row) => ({
      symptom: row.querySelector("[data-field=symptom]").value.trim(),
      days: row.querySelector("[data-field=days]").value.trim(),
    }))
    .filter((item) => item.symptom);
}

function setLastPrescriptionPrintUrl(url = "") {
  state.lastPrescriptionPrintUrl = url;
  const printButton = document.getElementById("print-prescription");
  if (!printButton) return;
  printButton.disabled = !url;
}

function bindIfPresent(id, eventName, handler) {
  const element = document.getElementById(id);
  if (element) element.addEventListener(eventName, handler);
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
  updateReceptionVitalsVisibility(document.getElementById("checkin-form"));
}

function formData(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function normalizeDepartment(value) {
  return String(value || "").toLowerCase().replace(/[^a-z]/g, "");
}

function departmentCategory(value) {
  const department = (state.session?.departments || []).find((item) => item.code === value);
  const haystack = `${value || ""} ${department?.name || ""}`;
  const normalized = normalizeDepartment(haystack);
  if (normalized.includes("ped")) return "peds";
  if (normalized.includes("gyn")) return "gynac";
  return "";
}

function departmentCodeForCategory(category) {
  return (state.session?.departments || []).find((item) => departmentCategory(item.code) === category)?.code || "";
}

function applyAgeDepartmentDefault(form) {
  const age = Number(form.age_years?.value);
  if (!Number.isFinite(age)) return;
  const targetCode = departmentCodeForCategory(age < 18 ? "peds" : "gynac");
  if (targetCode && form.department) {
    form.department.value = targetCode;
    updateReceptionVitalsVisibility(form);
  }
}

function updateReceptionVitalsVisibility(form) {
  if (!form) return;
  const category = departmentCategory(form.department?.value);
  const visibleFields = category === "peds"
    ? ["temperature_c", "height_cm", "weight_kg"]
    : category === "gynac"
      ? ["blood_pressure", "pulse_bpm", "weight_kg"]
      : ["temperature_c", "height_cm", "weight_kg", "blood_pressure", "pulse_bpm"];

  document.querySelectorAll("[data-vital-field]").forEach((field) => {
    const isVisible = visibleFields.includes(field.dataset.vitalField);
    field.classList.toggle("hidden", !isVisible);
    if (!isVisible) {
      const input = field.querySelector("input");
      if (input) input.value = "";
    }
  });
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

function visitHasPedsVitals(visit) {
  return visit.height_cm || visit.weight_kg || visit.temperature_c;
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

function canOpenAppointmentPrescription(appointment) {
  return state.session?.permissions?.prescription
    && sameLocalDate(new Date(appointment.scheduled_for), new Date())
    && appointment.status !== "COMPLETED"
    && appointment.status !== "CANCELLED";
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
      ? appointments.map((appointment) => {
        const canOpenPrescription = canOpenAppointmentPrescription(appointment);
        return `
        <article
          class="calendar-appointment ${canOpenPrescription ? "clickable" : ""}"
          ${canOpenPrescription ? `data-action="open-appointment-prescription" data-appointment-id="${escapeHtml(appointment.id)}" role="button" tabindex="0"` : ""}
        >
          <strong>${escapeHtml(formatCalendarTime(appointment.scheduled_for))} ${escapeHtml(appointment.patient.full_name)}</strong>
          <div class="meta">
            <span class="badge">${escapeHtml(departmentName(appointment.department))}</span>
            <span class="badge">${escapeHtml(appointment.status)}</span>
          </div>
          <div class="meta">${appointment.reason ? escapeHtml(appointment.reason) : "No reason entered"}</div>
        </article>
      `;
      }).join("")
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

function isCalendarActive() {
  return document.getElementById("view-calendar")?.classList.contains("active");
}

async function refreshActiveCalendar() {
  if (!state.session?.permissions?.calendar || !isCalendarActive() || document.hidden) return;
  if (state.calendarRefreshInFlight) return;

  state.calendarRefreshInFlight = true;
  try {
    await loadCalendarAppointments();
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    state.calendarRefreshInFlight = false;
  }
}

function startCalendarAutoRefresh() {
  if (!state.session?.permissions?.calendar || state.calendarRefreshTimer) return;
  state.calendarRefreshTimer = window.setInterval(() => {
    refreshActiveCalendar();
  }, CALENDAR_REFRESH_MS);
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
  if (queueList) queueList.innerHTML = html;
  if (prescriptionQueue) prescriptionQueue.innerHTML = html;
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
  if (!search.trim()) state.patientCache = data.patients;
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

function renderAppointmentPatientSuggestions(patients) {
  const menu = document.getElementById("appointment-patient-suggestions");
  state.appointmentPatientSuggestions = patients;
  if (!patients.length) {
    menu.classList.add("hidden");
    menu.innerHTML = "";
    return;
  }

  menu.innerHTML = patients.map((patient) => `
    <button class="autocomplete-option" data-action="select-appointment-patient" data-patient-id="${escapeHtml(patient.id)}" type="button">
      <strong>${escapeHtml(patient.full_name)}</strong>
      <span class="meta">${patient.phone_number ? escapeHtml(patient.phone_number) : "No mobile"} | ${escapeHtml(departmentName(patient.department))}</span>
    </button>
  `).join("");
  menu.classList.remove("hidden");
}

function renderLocalAppointmentPatientSuggestions(search) {
  const term = search.trim();
  const normalizedTerm = term.toLowerCase();
  if (!term) {
    renderAppointmentPatientSuggestions([]);
    return;
  }

  const localMatches = state.patientCache
    .filter((patient) => patient.full_name.toLowerCase().startsWith(normalizedTerm))
    .slice(0, 8);
  renderAppointmentPatientSuggestions(localMatches);
}

async function searchAppointmentPatients(search) {
  if (!state.session?.permissions?.patients) return;
  const term = search.trim();
  const normalizedTerm = term.toLowerCase();
  if (!term) {
    renderAppointmentPatientSuggestions([]);
    return;
  }

  const token = ++state.appointmentPatientSearchToken;
  const data = await http.request(`/api/patients/?search=${encodeURIComponent(term)}`);
  if (token !== state.appointmentPatientSearchToken) return;
  renderAppointmentPatientSuggestions(
    data.patients
      .filter((patient) => patient.full_name.toLowerCase().startsWith(normalizedTerm))
      .slice(0, 8)
  );
}

function selectAppointmentPatient(patientId) {
  const patient = state.appointmentPatientSuggestions.find((item) => String(item.id) === String(patientId));
  if (!patient) return;
  const form = document.getElementById("appointment-form");
  form.full_name.value = patient.full_name;
  form.phone_number.value = patient.phone_number || "";
  form.department.value = patient.department;
  renderAppointmentPatientSuggestions([]);
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
      <div class="meta">Dr. ${escapeHtml(item.doctor_name)} | ${item.symptoms ? escapeHtml(item.symptoms) : "No symptoms entered"}</div>
      <div class="meta">${item.diagnosis ? `Diagnosis: ${escapeHtml(item.diagnosis)}` : "No diagnosis entered"}</div>
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
  const medicineList = document.getElementById("medicine-list");
  if (!medicineList) return;
  const row = document.createElement("div");
  row.className = "medicine-row";
  row.innerHTML = `
    <input name="medicine_name" placeholder="Medicine" value="${escapeHtml(values.medicine_name || "")}">
    <input name="dosage" placeholder="Dosage" value="${escapeHtml(values.dosage || "")}">
    <input name="frequency" placeholder="Frequency" value="${escapeHtml(values.frequency || "")}">
    <input name="duration" placeholder="Duration" value="${escapeHtml(values.duration || "")}">
    <input name="instructions" placeholder="Instructions" value="${escapeHtml(values.instructions || "")}">
  `;
  medicineList.appendChild(row);
}

function setDoctorVitalsVisibility(visit) {
  const panel = document.getElementById("doctor-vitals-panel");
  const form = document.getElementById("visit-vitals-form");
  if (!panel || !form || !visit) return;

  const category = departmentCategory(visit.department);
  const visibleFields = category === "peds"
    ? ["temperature_c", "height_cm", "weight_kg"]
    : category === "gynac"
      ? ["blood_pressure", "pulse_bpm", "weight_kg"]
      : ["temperature_c", "height_cm", "weight_kg", "blood_pressure", "pulse_bpm"];

  panel.classList.remove("hidden");
  form.temperature_c.value = visit.temperature_c || "";
  form.height_cm.value = visit.height_cm || "";
  form.weight_kg.value = visit.weight_kg || "";
  form.blood_pressure.value = visit.blood_pressure || "";
  form.pulse_bpm.value = visit.pulse_bpm || "";

  document.querySelectorAll("[data-doctor-vital-field]").forEach((field) => {
    field.classList.toggle("hidden", !visibleFields.includes(field.dataset.doctorVitalField));
  });
}

function renderGrowthChart(visits) {
  const container = document.getElementById("growth-chart");
  if (!container) return;
  const points = visits
    .filter((visit) => visitHasPedsVitals(visit))
    .slice()
    .reverse();

  if (!points.length) {
    container.innerHTML = `<div class="meta">No pediatric vitals recorded yet.</div>`;
    return;
  }

  const metrics = [
    { key: "height_cm", label: "Height cm", color: "#176b70" },
    { key: "weight_kg", label: "Weight kg", color: "#8a4f1d" },
    { key: "temperature_c", label: "Temp C", color: "#9b1c31" },
  ];
  const width = 640;
  const height = 220;
  const padding = 28;
  const x = (index) => points.length === 1
    ? width / 2
    : padding + (index * (width - padding * 2)) / (points.length - 1);
  const lines = metrics.map((metric) => {
    const values = points
      .map((visit, index) => ({ value: Number(visit[metric.key]), index }))
      .filter((item) => Number.isFinite(item.value));
    if (!values.length) return "";
    const min = Math.min(...values.map((item) => item.value));
    const max = Math.max(...values.map((item) => item.value));
    const span = max - min || 1;
    const y = (value) => height - padding - ((value - min) * (height - padding * 2)) / span;
    const path = values.map((item) => `${x(item.index)},${y(item.value)}`).join(" ");
    const circles = values.map((item) => `<circle cx="${x(item.index)}" cy="${y(item.value)}" r="4" fill="${metric.color}"><title>${escapeHtml(metric.label)}: ${escapeHtml(item.value)}</title></circle>`).join("");
    return `<polyline points="${path}" fill="none" stroke="${metric.color}" stroke-width="2"></polyline>${circles}`;
  }).join("");

  container.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Growth chart">
      <line x1="${padding}" y1="${height - padding}" x2="${width - padding}" y2="${height - padding}" stroke="#9aa8b3"></line>
      <line x1="${padding}" y1="${padding}" x2="${padding}" y2="${height - padding}" stroke="#9aa8b3"></line>
      ${lines}
    </svg>
    <div class="chart-legend">
      ${metrics.map((metric) => `<span class="meta"><span style="color:${metric.color}; font-weight:800;">■</span> ${escapeHtml(metric.label)}</span>`).join("")}
    </div>
  `;
}

async function loadSelectedVisitHistory() {
  if (!state.selectedVisit) return;
  setDoctorVitalsVisibility(state.selectedVisit);
  if (departmentCategory(state.selectedVisit.department) !== "peds") {
    const chart = document.getElementById("growth-chart");
    if (chart) chart.innerHTML = `<div class="meta">Growth chart is shown for pediatric visits.</div>`;
    return;
  }
  const data = await http.request(`/api/patients/${encodeURIComponent(state.selectedVisit.patient.id)}/history/`);
  renderGrowthChart(data.visits || []);
}

function selectVisit(visitId) {
  const visit = state.queue.find((item) => String(item.id) === String(visitId));
  if (!visit) return;
  state.selectedVisit = visit;
  const form = document.getElementById("prescription-form");
  form.patient_id.value = visit.patient.id;
  form.visit_id.value = visit.id;
  setLastPrescriptionPrintUrl("");
  document.getElementById("selected-patient-label").textContent = visit.patient.full_name;
  switchView("prescription");
  loadSelectedVisitHistory().catch((error) => setStatus(error.message, true));
}

async function openAppointmentPrescription(appointmentId) {
  const appointment = state.calendarAppointments.find((item) => String(item.id) === String(appointmentId));
  if (!appointment) return;
  if (!canOpenAppointmentPrescription(appointment)) {
    setStatus("Only today's active appointments can be opened for prescription.", true);
    return;
  }

  setStatus("Opening prescription...");
  await loadQueue();
  const activeVisits = state.queue.filter((visit) => String(visit.patient.id) === String(appointment.patient.id));
  const visit = activeVisits.find((item) =>
    item.department === appointment.department && item.reason === appointment.reason
  ) || activeVisits[0];

  if (!visit) {
    setStatus("No active consultation visit was found for this appointment.", true);
    return;
  }

  selectVisit(visit.id);
  setStatus("Ready for prescription");
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
  let appointmentPatientSearchTimer = null;

  document.querySelectorAll(".nav-item[data-view]").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view));
  });

  document.body.addEventListener("click", (event) => {
    const appointmentCard = event.target.closest("[data-action='open-appointment-prescription']");
    if (appointmentCard) {
      openAppointmentPrescription(appointmentCard.dataset.appointmentId).catch((error) => setStatus(error.message, true));
      return;
    }
    if (event.target.dataset.action === "consult") {
      selectVisit(event.target.dataset.visitId);
    }
    if (event.target.dataset.action === "remove-symptom") {
      event.target.closest(".symptom-row")?.remove();
    }
    if (event.target.closest("[data-action='view-patient']")) {
      const row = event.target.closest("[data-action='view-patient']");
      openPatientDetail(row.dataset.patientId).catch((error) => setStatus(error.message, true));
    }
    if (event.target.dataset.action === "print-prescription") {
      window.open(event.target.dataset.printUrl, "_blank", "noopener");
    }
    if (event.target.dataset.action === "select-appointment-patient") {
      selectAppointmentPatient(event.target.dataset.patientId);
    }
  });

  document.body.addEventListener("keydown", (event) => {
    const appointmentCard = event.target.closest("[data-action='open-appointment-prescription']");
    if (!appointmentCard || (event.key !== "Enter" && event.key !== " ")) return;
    event.preventDefault();
    openAppointmentPrescription(appointmentCard.dataset.appointmentId).catch((error) => setStatus(error.message, true));
  });

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".autocomplete-field")) {
      renderAppointmentPatientSuggestions([]);
    }
  });

  bindIfPresent("refresh-queue", "click", loadQueue);
  bindIfPresent("refresh-appointments", "click", loadAppointments);
  window.addEventListener("focus", () => {
    refreshActiveCalendar();
  });
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) refreshActiveCalendar();
  });
  bindIfPresent("previous-week", "click", () => {
    state.calendarWeekStart = addDays(state.calendarWeekStart || startOfWeek(new Date()), -7);
    loadCalendarAppointments().catch((error) => setStatus(error.message, true));
  });
  bindIfPresent("current-week", "click", () => {
    state.calendarWeekStart = startOfWeek(new Date());
    loadCalendarAppointments().catch((error) => setStatus(error.message, true));
  });
  bindIfPresent("next-week", "click", () => {
    state.calendarWeekStart = addDays(state.calendarWeekStart || startOfWeek(new Date()), 7);
    loadCalendarAppointments().catch((error) => setStatus(error.message, true));
  });
  bindIfPresent("close-patient-detail", "click", () => {
    document.getElementById("patient-detail")?.classList.add("hidden");
    state.selectedPatientId = null;
  });
  bindIfPresent("add-medicine", "click", () => addMedicineRow());
  bindIfPresent("add-symptom", "click", addSymptom);
  bindIfPresent("symptom-input", "keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      addSymptom();
    }
  });
  bindIfPresent("symptom-days-input", "keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      addSymptom();
    }
  });
  bindIfPresent("print-prescription", "click", () => {
    if (state.lastPrescriptionPrintUrl) window.open(state.lastPrescriptionPrintUrl, "_blank", "noopener");
  });

  bindIfPresent("patient-search", "input", (event) => {
    loadPatients(event.target.value).catch((error) => setStatus(error.message, true));
  });

  bindIfPresent("checkin-form", "input", (event) => {
    if (event.target.name === "age_years") applyAgeDepartmentDefault(event.currentTarget);
  });
  bindIfPresent("checkin-form", "change", (event) => {
    if (event.target.name === "department") updateReceptionVitalsVisibility(event.currentTarget);
  });
  bindIfPresent("appointment-form", "input", (event) => {
    if (event.target.name === "age_years") applyAgeDepartmentDefault(event.currentTarget);
  });

  bindIfPresent("appointment-patient-name", "input", (event) => {
    window.clearTimeout(appointmentPatientSearchTimer);
    renderLocalAppointmentPatientSuggestions(event.target.value);
    appointmentPatientSearchTimer = window.setTimeout(() => {
      searchAppointmentPatients(event.target.value).catch((error) => setStatus(error.message, true));
    }, 60);
  });

  bindIfPresent("checkin-form", "submit", async (event) => {
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
      updateReceptionVitalsVisibility(event.target);
      setStatus("Checked in");
    } catch (error) {
      setStatus(error.message, true);
    }
  });

  bindIfPresent("appointment-form", "submit", async (event) => {
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

  bindIfPresent("prescription-form", "submit", async (event) => {
    event.preventDefault();
    try {
      const data = formData(event.target);
      data.patient_id = Number(data.patient_id);
      data.visit_id = data.visit_id ? Number(data.visit_id) : null;
      data.symptom_entries = symptomEntries();
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
      setLastPrescriptionPrintUrl(result.print_url);
      setStatus("Prescription saved");
    } catch (error) {
      setStatus(error.message, true);
    }
  });

  bindIfPresent("visit-vitals-form", "submit", async (event) => {
    event.preventDefault();
    if (!state.selectedVisit) return;
    try {
      const result = await http.request(`/api/visits/${encodeURIComponent(state.selectedVisit.id)}/vitals/`, {
        method: "PATCH",
        body: JSON.stringify(formData(event.target)),
      });
      state.selectedVisit = result.visit;
      state.queue = state.queue.map((visit) => String(visit.id) === String(result.visit.id) ? result.visit : visit);
      await loadSelectedVisitHistory();
      setStatus("Vitals saved");
    } catch (error) {
      setStatus(error.message, true);
    }
  });

  bindIfPresent("bill-form", "submit", async (event) => {
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
  startCalendarAutoRefresh();
  addMedicineRow({ frequency: "1-0-1" });
  await Promise.all([loadQueue(), loadPatients(), loadAppointments(), loadCalendarAppointments()]);
}

start().catch((error) => setStatus(error.message, true));
