import fs from "node:fs/promises";
import path from "node:path";
import playwright from "../build/demo-video/node_modules/playwright/index.js";

const { chromium } = playwright;

const root = path.resolve(import.meta.dirname, "../..");
const videoDir = path.join(root, "lib", "dist", "demo-video");
const chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const baseUrl = process.env.DEMO_BASE_URL || "http://127.0.0.1:8020";

await fs.mkdir(videoDir, { recursive: true });

const browser = await chromium.launch({
  executablePath: chromePath,
  headless: true,
});
const context = await browser.newContext({
  viewport: { width: 1366, height: 768 },
  recordVideo: {
    dir: videoDir,
    size: { width: 1366, height: 768 },
  },
});
const page = await context.newPage();

async function caption(text) {
  await page.evaluate((message) => {
    let el = document.getElementById("demo-caption");
    if (!el) {
      el = document.createElement("div");
      el.id = "demo-caption";
      el.style.position = "fixed";
      el.style.left = "24px";
      el.style.bottom = "24px";
      el.style.zIndex = "99999";
      el.style.maxWidth = "780px";
      el.style.padding = "14px 18px";
      el.style.borderRadius = "8px";
      el.style.background = "rgba(18, 50, 54, 0.94)";
      el.style.color = "#fff";
      el.style.font = "600 20px/1.35 Segoe UI, Arial, sans-serif";
      el.style.boxShadow = "0 14px 40px rgba(0,0,0,.28)";
      document.body.appendChild(el);
    }
    el.textContent = message;
  }, text);
  await page.waitForTimeout(1800);
}

async function login(username, password) {
  await page.goto(`${baseUrl}/login/`);
  await page.locator("input[name=username]").fill(username);
  await page.locator("input[name=password]").fill(password);
  await page.locator("button[type=submit]").click();
  await page.waitForLoadState("networkidle");
}

async function logout() {
  await page.locator("form[action='/logout/'] button").click();
  await page.waitForLoadState("networkidle");
}

async function clickNav(viewName) {
  await page.locator(`.nav-item[data-view="${viewName}"]`).click();
  await page.waitForTimeout(500);
}

await login("reception", "Reception@123");
await caption("Reception view: fast patient check-in, waiting queue, appointments, and patient search.");

await clickNav("desk");
await caption("Quick Check-In captures minimum patient details and adds the patient to the waiting queue.");
await page.locator("#checkin-form input[name=full_name]").fill("Demo Patient");
await page.locator("#checkin-form input[name=phone_number]").fill("9000010099");
await page.locator("#checkin-form input[name=reason]").fill("Fever and follow-up");
await page.locator("#checkin-form button[type=submit]").click();
await page.waitForTimeout(1200);
await caption("The waiting queue updates immediately for reception and doctors.");

await clickNav("appointments");
await caption("Appointments: existing patient names autocomplete, and selecting one fills the mobile number.");
await page.locator("#appointment-patient-name").fill("An");
await page.waitForTimeout(900);
await page.locator("#appointment-patient-suggestions .autocomplete-option").first().click();
await page.waitForTimeout(800);
const tomorrow = new Date(Date.now() + 24 * 60 * 60 * 1000);
tomorrow.setHours(11, 0, 0, 0);
const slot = `${tomorrow.getFullYear()}-${String(tomorrow.getMonth() + 1).padStart(2, "0")}-${String(tomorrow.getDate()).padStart(2, "0")}T11:00`;
await page.locator("#appointment-form input[name=scheduled_for]").fill(slot);
await page.locator("#appointment-form input[name=reason]").fill("Demo follow-up appointment");
await caption("Appointment start time is used for scheduling and conflict checking.");
await page.locator("#appointment-form button[type=submit]").click();
await page.waitForTimeout(1400);
await caption("The upcoming list shows scheduled appointments with patient, department, time, and reason.");

await logout();
await login("doctor", "Doctor@123");
await caption("Doctor view opens directly to the weekly calendar.");
await clickNav("calendar");
await caption("Doctors can move week by week, similar to an Outlook calendar.");
await page.locator("#next-week").click();
await page.waitForTimeout(900);
await page.locator("#current-week").click();
await page.waitForTimeout(900);

await clickNav("prescription");
await caption("Doctors can select a patient from the consultation queue and create a prescription.");
await page.locator("#prescription-queue [data-action='consult']").first().click();
await page.waitForTimeout(800);
await page.locator("#prescription-form input[name=doctor_name]").fill("Dr. Demo");
await page.locator("#diagnosis-symptom-input").fill("Fever");
await page.locator("#add-diagnosis-symptom").click();
await page.locator("#prescription-form textarea[name=advice]").fill("Hydration, rest, and review if symptoms increase.");
await caption("Prescription entry supports symptoms, advice, medicines, saving, and printing.");

await logout();
await login("admin", "Admin@123");
await caption("Admin users manage hospital configuration, users, departments, appointment duration, and backups.");
await page.goto(`${baseUrl}/admin/`);
await page.waitForLoadState("networkidle");
await caption("The admin home now previews existing records under each category.");
await page.goto(`${baseUrl}/admin/repository/backuprecord/`);
await page.waitForLoadState("networkidle");
await caption("Backups are created from Backup records after the backup folder is configured in Hospital profile.");

await page.goto(`${baseUrl}/`);
await page.waitForLoadState("networkidle");
await caption("Hospital Information Management System: local server, browser access over LAN, role-based workflows.");

const video = page.video();
await context.close();
await browser.close();

const savedPath = await video.path();
const finalPath = path.join(videoDir, "hospital-demo-flows.webm");
await fs.copyFile(savedPath, finalPath);
console.log(finalPath);
