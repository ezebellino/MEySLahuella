import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "./api";

const defaultHostForm = {
  name: "",
  address: "",
  port: 445,
  username: "",
  password: "",
  host_type: "windows",
  winrm_port: 5985,
  base_path: "C:\\",
  restart_command: "shutdown /r /t 5 /f"
};

const defaultCandidates = [
  { username: "LAHUELLA\\Via", password: "" },
  { username: "LAHUELLA\\administrator", password: "" }
];

const steps = [
  { id: 1, title: "Red y Diagnóstico" },
  { id: 2, title: "Hosts y Credenciales" },
  { id: 3, title: "Operación Remota" }
];

const topologyDeviceTemplate = [
  { key: "antenna", label: "Antena TelePASE" },
  { key: "pc", label: "PC de vía" },
  { key: "printer", label: "Impresora" },
  { key: "camera_surveillance", label: "Cámara vigilancia" },
  { key: "camera_ocr", label: "Cámara OCR" }
];

const defaultOperationTemplates = [
  {
    id: "tpl-vias-51-55",
    name: "Vías 51-55",
    target_addresses: ["10.95.25.151", "10.95.25.152", "10.95.25.153", "10.95.25.154", "10.95.25.155"],
    command: "hostname",
    file_path: "C:\\",
    remote_path: "C:\\Temp\\lahuella_sync.txt",
    transfer_content: "DATOS DE PRUEBA SISTEMAS LA HUELLA",
    updated_at: "",
  },
  {
    id: "tpl-vias-07-11",
    name: "Vías 07-11",
    target_addresses: ["10.95.25.107", "10.95.25.108", "10.95.25.109", "10.95.25.110", "10.95.25.111"],
    command: "hostname",
    file_path: "C:\\",
    remote_path: "C:\\Temp\\lahuella_sync.txt",
    transfer_content: "DATOS DE PRUEBA SISTEMAS LA HUELLA",
    updated_at: "",
  },
];

function createDefaultTopology(hostName = "") {
  return {
    switch_name: hostName ? `Switch ${hostName}` : "Switch principal",
    switch_ip: "",
    switch_model: "",
    switch_location: "",
    notes: "",
    devices: topologyDeviceTemplate.map((item) => ({
      ...item,
      port: "",
      ip: "",
      hostname: "",
      status: "unknown",
      notes: ""
    }))
  };
}

function sanitizeTemplateForStorage(template) {
  return {
    id: template.id,
    name: template.name,
    target_addresses: Array.isArray(template.target_addresses) ? template.target_addresses : [],
    file_path: template.file_path || "C:\\",
    remote_path: template.remote_path || "C:\\Temp\\lahuella_sync.txt",
    updated_at: template.updated_at || "",
  };
}

function hydrateTemplateFromStorage(template) {
  return {
    id: template.id || `tpl-${Date.now()}`,
    name: template.name || "Plantilla",
    target_addresses: Array.isArray(template.target_addresses) ? template.target_addresses : [],
    command: "hostname",
    file_path: template.file_path || "C:\\",
    remote_path: template.remote_path || "C:\\Temp\\lahuella_sync.txt",
    transfer_content: "",
    updated_at: template.updated_at || "",
  };
}

function statusText(check) {
  if (!check) return "Sin prueba";
  if (!check.reachable) return check._retried ? "Sin conexión (reintento)" : "Sin conexión";
  if (check.auth_success === false) return check._retried ? "Credencial inválida (reintento)" : "Credencial inválida";
  if (check.ready) return check._retried ? "Listo (reintento)" : "Listo para operar";
  return "Parcial";
}

function readStorage(key, fallback) {
  try {
    const raw = window.localStorage.getItem(key);
    if (raw === null) return fallback;
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

export default function App() {
  const [showHero, setShowHero] = useState(() => readStorage("lh_show_hero", true));
  const [operationMode, setOperationMode] = useState(() => readStorage("lh_operation_mode", false));
  const [compactMode, setCompactMode] = useState(() => readStorage("lh_compact_mode", false));
  const [cabinaMode, setCabinaMode] = useState(() => readStorage("lh_cabina_mode", false));
  const [autoRefresh, setAutoRefresh] = useState(() => readStorage("lh_auto_refresh", false));
  const [alertsEnabled, setAlertsEnabled] = useState(() => readStorage("lh_alerts_enabled", true));
  const [alertSoundEnabled, setAlertSoundEnabled] = useState(() => readStorage("lh_alert_sound", false));
  const [alertsSilencedUntil, setAlertsSilencedUntil] = useState(() =>
    readStorage("lh_alerts_silenced_until", "")
  );
  const [refreshSeconds, setRefreshSeconds] = useState(() => readStorage("lh_refresh_seconds", 45));
  const [lastRefreshAt, setLastRefreshAt] = useState(() => readStorage("lh_last_refresh_at", ""));
  const [step, setStep] = useState(() => readStorage("lh_step", 1));
  const [systemInfo, setSystemInfo] = useState(null);
  const [antenna, setAntenna] = useState(null);
  const [tags, setTags] = useState([]);
  const [hosts, setHosts] = useState([]);
  const [hostChecks, setHostChecks] = useState({});
  const [hostForm, setHostForm] = useState(defaultHostForm);
  const [editingHostId, setEditingHostId] = useState(null);
  const [hostModalOpen, setHostModalOpen] = useState(false);
  const [selectedHostId, setSelectedHostId] = useState(null);
  const [search, setSearch] = useState(() => readStorage("lh_search", ""));
  const [statusFilter, setStatusFilter] = useState(() => readStorage("lh_status_filter", "all"));

  const [filePath, setFilePath] = useState("C:\\");
  const [fileItems, setFileItems] = useState([]);
  const [command, setCommand] = useState("hostname");
  const [remotePath, setRemotePath] = useState("C:\\Temp\\lahuella_sync.txt");
  const [transferContent, setTransferContent] = useState("DATOS DE PRUEBA SISTEMAS LA HUELLA");
  const [downloadContent, setDownloadContent] = useState("");
  const [opTemplates, setOpTemplates] = useState(() => {
    const saved = readStorage("lh_op_templates", []);
    return Array.isArray(saved) && saved.length
      ? saved.map((item) => hydrateTemplateFromStorage(item))
      : defaultOperationTemplates;
  });
  const [selectedTemplateId, setSelectedTemplateId] = useState(() =>
    readStorage("lh_op_template_selected", "")
  );
  const [templateName, setTemplateName] = useState(() => readStorage("lh_tpl_name", ""));
  const [templateTargetsText, setTemplateTargetsText] = useState(() =>
    readStorage("lh_tpl_targets_text", "")
  );
  const [batchResults, setBatchResults] = useState([]);
  const [batchRunning, setBatchRunning] = useState(false);
  const [criticalGuardEnabled, setCriticalGuardEnabled] = useState(() =>
    readStorage("lh_critical_guard_enabled", true)
  );
  const [criticalUnlockedUntil, setCriticalUnlockedUntil] = useState(() =>
    readStorage("lh_critical_unlocked_until", "")
  );

  const [potenciaInput, setPotenciaInput] = useState("");
  const [sourcePath, setSourcePath] = useState("C:\\Via\\Aplicacion");
  const [destinationPath, setDestinationPath] = useState("");
  const [discoverSubnet, setDiscoverSubnet] = useState(() => readStorage("lh_subnet", "10.95.25.0/24"));
  const [discoverPort, setDiscoverPort] = useState(() => readStorage("lh_port", 445));
  const [discovered, setDiscovered] = useState([]);
  const [credentialCandidates, setCredentialCandidates] = useState(defaultCandidates);
  const [credentialResults, setCredentialResults] = useState([]);
  const [rotateUser, setRotateUser] = useState("LAHUELLA\\Via");
  const [rotatePassword, setRotatePassword] = useState("");
  const [rotationHistory, setRotationHistory] = useState([]);
  const [auditEvents, setAuditEvents] = useState([]);
  const [auditHostScope, setAuditHostScope] = useState(() => readStorage("lh_audit_scope", "selected"));
  const [auditTypeFilter, setAuditTypeFilter] = useState(() => readStorage("lh_audit_type", "all"));
  const [auditStatusFilter, setAuditStatusFilter] = useState(() => readStorage("lh_audit_status", "all"));
  const [auditDateFrom, setAuditDateFrom] = useState(() => readStorage("lh_audit_from", ""));
  const [auditDateTo, setAuditDateTo] = useState(() => readStorage("lh_audit_to", ""));
  const [auditLoading, setAuditLoading] = useState(false);
  const [expandedAuditKey, setExpandedAuditKey] = useState("");
  const [hostTopology, setHostTopology] = useState(() => createDefaultTopology());
  const [topologyLoading, setTopologyLoading] = useState(false);
  const [status, setStatus] = useState("Sistema listo");
  const [loading, setLoading] = useState(false);
  const monitorLockRef = useRef(false);
  const lastAlertSignatureRef = useRef("");

  const selectedHost = useMemo(
    () => hosts.find((host) => host.id === selectedHostId) ?? null,
    [hosts, selectedHostId]
  );

  const filteredHosts = useMemo(() => {
    const q = search.trim().toLowerCase();
    return hosts
      .filter((host) => {
        if (!q) return true;
        return (
          host.name.toLowerCase().includes(q) ||
          host.address.toLowerCase().includes(q) ||
          host.username.toLowerCase().includes(q)
        );
      })
      .filter((host) => {
        const c = hostChecks[host.id];
        if (statusFilter === "all") return true;
        if (statusFilter === "ready") return c?.ready;
        if (statusFilter === "offline") return c ? !c.reachable : false;
        if (statusFilter === "auth_fail") return c?.auth_success === false;
        return true;
      });
  }, [hosts, hostChecks, search, statusFilter]);

  const summary = useMemo(() => {
    const total = hosts.length;
    const tested = hosts.filter((h) => !!hostChecks[h.id]).length;
    const ready = hosts.filter((h) => hostChecks[h.id]?.ready).length;
    const offline = hosts.filter((h) => {
      const c = hostChecks[h.id];
      return c ? !c.reachable : false;
    }).length;
    const authFail = hosts.filter((h) => hostChecks[h.id]?.auth_success === false).length;
    return { total, tested, ready, offline, authFail };
  }, [hosts, hostChecks]);

  const alerts = useMemo(() => {
    const items = [];
    for (const host of hosts) {
      const check = hostChecks[host.id];
      if (!check) continue;

      if (!check.reachable) {
        items.push({
          id: `${host.id}-offline`,
          hostId: host.id,
          hostName: host.name,
          hostAddress: host.address,
          level: "critical",
          code: "host_offline",
          text: "Host sin conexión",
        });
      }

      if (check.auth_success === false) {
        items.push({
          id: `${host.id}-auth`,
          hostId: host.id,
          hostName: host.name,
          hostAddress: host.address,
          level: "warning",
          code: "auth_fail",
          text: "Credencial inválida",
        });
      }

      if (check.smb_open === false) {
        items.push({
          id: `${host.id}-smb`,
          hostId: host.id,
          hostName: host.name,
          hostAddress: host.address,
          level: "warning",
          code: "smb_closed",
          text: "Puerto SMB cerrado (445)",
        });
      }

      if (host.host_type === "windows" && check.winrm_open === false) {
        items.push({
          id: `${host.id}-winrm`,
          hostId: host.id,
          hostName: host.name,
          hostAddress: host.address,
          level: "warning",
          code: "winrm_closed",
          text: "Puerto WinRM cerrado",
        });
      }
    }
    return items;
  }, [hosts, hostChecks]);

  const criticalAlerts = alerts.filter((item) => item.level === "critical").length;
  const warningAlerts = alerts.filter((item) => item.level === "warning").length;
  const alertsSilenced = useMemo(() => {
    if (!alertsSilencedUntil) return false;
    const ts = new Date(alertsSilencedUntil).getTime();
    if (!Number.isFinite(ts)) return false;
    return ts > Date.now();
  }, [alertsSilencedUntil]);

  const activeAlertSignature = useMemo(
    () => alerts.map((item) => `${item.code}:${item.hostId}`).sort().join("|"),
    [alerts]
  );

  const criticalUnlocked = useMemo(() => {
    if (!criticalGuardEnabled) return true;
    const ts = new Date(criticalUnlockedUntil || "").getTime();
    return Number.isFinite(ts) && ts > Date.now();
  }, [criticalGuardEnabled, criticalUnlockedUntil]);

  async function loadDashboard() {
    setLoading(true);
    try {
      const [system, antennaData, tagsData, hostsData] = await Promise.all([
        api.systemInfo(),
        api.antenna(),
        api.tags(),
        api.hosts()
      ]);
      setSystemInfo(system);
      setAntenna(antennaData);
      setPotenciaInput(antennaData.potencia || "");
      setTags(tagsData.items || []);
      setHosts(hostsData.items || []);
      if (!selectedHostId && hostsData.items?.length) {
        setSelectedHostId(hostsData.items[0].id);
      }
      setStatus("Panel actualizado");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  useEffect(() => {
    window.localStorage.setItem("lh_step", JSON.stringify(step));
  }, [step]);

  useEffect(() => {
    window.localStorage.setItem("lh_search", JSON.stringify(search));
  }, [search]);

  useEffect(() => {
    window.localStorage.setItem("lh_status_filter", JSON.stringify(statusFilter));
  }, [statusFilter]);

  useEffect(() => {
    window.localStorage.setItem("lh_subnet", JSON.stringify(discoverSubnet));
  }, [discoverSubnet]);

  useEffect(() => {
    window.localStorage.setItem("lh_port", JSON.stringify(Number(discoverPort) || 445));
  }, [discoverPort]);

  useEffect(() => {
    window.localStorage.setItem("lh_show_hero", JSON.stringify(showHero));
  }, [showHero]);

  useEffect(() => {
    window.localStorage.setItem("lh_operation_mode", JSON.stringify(operationMode));
  }, [operationMode]);

  useEffect(() => {
    window.localStorage.setItem("lh_compact_mode", JSON.stringify(compactMode));
  }, [compactMode]);

  useEffect(() => {
    window.localStorage.setItem("lh_cabina_mode", JSON.stringify(cabinaMode));
  }, [cabinaMode]);

  useEffect(() => {
    window.localStorage.setItem("lh_auto_refresh", JSON.stringify(autoRefresh));
  }, [autoRefresh]);

  useEffect(() => {
    window.localStorage.setItem("lh_alerts_enabled", JSON.stringify(alertsEnabled));
  }, [alertsEnabled]);

  useEffect(() => {
    window.localStorage.setItem("lh_alert_sound", JSON.stringify(alertSoundEnabled));
  }, [alertSoundEnabled]);

  useEffect(() => {
    window.localStorage.setItem("lh_alerts_silenced_until", JSON.stringify(alertsSilencedUntil));
  }, [alertsSilencedUntil]);

  useEffect(() => {
    window.localStorage.setItem("lh_refresh_seconds", JSON.stringify(Number(refreshSeconds) || 45));
  }, [refreshSeconds]);

  useEffect(() => {
    window.localStorage.setItem("lh_last_refresh_at", JSON.stringify(lastRefreshAt));
  }, [lastRefreshAt]);

  useEffect(() => {
    window.localStorage.setItem(
      "lh_op_templates",
      JSON.stringify(opTemplates.map((item) => sanitizeTemplateForStorage(item)))
    );
  }, [opTemplates]);

  useEffect(() => {
    window.localStorage.setItem("lh_op_template_selected", JSON.stringify(selectedTemplateId));
  }, [selectedTemplateId]);

  useEffect(() => {
    window.localStorage.setItem("lh_tpl_name", JSON.stringify(templateName));
  }, [templateName]);

  useEffect(() => {
    window.localStorage.setItem("lh_tpl_targets_text", JSON.stringify(templateTargetsText));
  }, [templateTargetsText]);

  useEffect(() => {
    window.localStorage.setItem("lh_critical_guard_enabled", JSON.stringify(criticalGuardEnabled));
  }, [criticalGuardEnabled]);

  useEffect(() => {
    window.localStorage.setItem("lh_critical_unlocked_until", JSON.stringify(criticalUnlockedUntil));
  }, [criticalUnlockedUntil]);

  useEffect(() => {
    if (!selectedTemplateId) return;
    const tpl = opTemplates.find((item) => item.id === selectedTemplateId);
    if (!tpl) return;
    if (!templateName) setTemplateName(tpl.name || "");
    if (!templateTargetsText) setTemplateTargetsText((tpl.target_addresses || []).join("\n"));
  }, [selectedTemplateId, opTemplates, templateName, templateTargetsText]);

  useEffect(() => {
    window.localStorage.setItem("lh_audit_scope", JSON.stringify(auditHostScope));
  }, [auditHostScope]);

  useEffect(() => {
    window.localStorage.setItem("lh_audit_type", JSON.stringify(auditTypeFilter));
  }, [auditTypeFilter]);

  useEffect(() => {
    window.localStorage.setItem("lh_audit_status", JSON.stringify(auditStatusFilter));
  }, [auditStatusFilter]);

  useEffect(() => {
    window.localStorage.setItem("lh_audit_from", JSON.stringify(auditDateFrom));
  }, [auditDateFrom]);

  useEffect(() => {
    window.localStorage.setItem("lh_audit_to", JSON.stringify(auditDateTo));
  }, [auditDateTo]);

  useEffect(() => {
    if (selectedHostId) {
      loadRotationHistory(selectedHostId);
      loadHostTopology(selectedHostId);
    } else {
      setHostTopology(createDefaultTopology());
    }
  }, [selectedHostId]);

  async function quickCheckHost(hostId, includeAuth = true) {
    try {
      const check = await api.quickCheckHost(hostId, includeAuth);
      const merged = { ...check, _retried: Boolean(check?._meta?.retried) };
      setHostChecks((prev) => ({ ...prev, [hostId]: merged }));
      return merged;
    } catch (error) {
      setHostChecks((prev) => ({
        ...prev,
        [hostId]: { reachable: false, auth_success: false, auth_error: error.message, ready: false }
      }));
      return null;
    }
  }

  async function quickCheckAll() {
    setLoading(true);
    try {
      const checks = await Promise.all(hosts.map((h) => quickCheckHost(h.id, true)));
      const ok = checks.filter((c) => c?.ready).length;
      setStatus(`Chequeo completo: ${ok}/${hosts.length} listos para operar.`);
    } finally {
      setLoading(false);
    }
  }

  async function monitorNow() {
    if (monitorLockRef.current) return;
    monitorLockRef.current = true;
    setLoading(true);
    try {
      const hostsData = (await api.hosts()).items || [];
      setHosts(hostsData);
      if (!selectedHostId && hostsData.length) {
        setSelectedHostId(hostsData[0].id);
      }
      const checks = await Promise.all(
        hostsData.map(async (host) => {
          try {
            const check = await api.quickCheckHost(host.id, true);
            return [host.id, { ...check, _retried: Boolean(check?._meta?.retried) }];
          } catch (error) {
            return [
              host.id,
              { reachable: false, auth_success: false, auth_error: error.message, ready: false }
            ];
          }
        })
      );
      const checkMap = {};
      for (const [id, check] of checks) {
        checkMap[id] = check;
      }
      setHostChecks(checkMap);
      const ok = checks.filter(([, check]) => check?.ready).length;
      const retried = checks.filter(([, check]) => check?._retried).length;
      const stamp = new Date().toLocaleTimeString();
      setLastRefreshAt(stamp);
      setStatus(
        `Monitor: ${ok}/${hostsData.length} listos (${stamp})${retried ? ` | reintentos: ${retried}` : ""}.`
      );
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
      monitorLockRef.current = false;
    }
  }

  useEffect(() => {
    if (!autoRefresh || showHero) return;
    const intervalSec = Math.max(15, Number(refreshSeconds) || 45);
    const timer = setInterval(() => {
      if (document.hidden) return;
      monitorNow();
    }, intervalSec * 1000);
    return () => clearInterval(timer);
  }, [autoRefresh, refreshSeconds, showHero]);

  useEffect(() => {
    if (!activeAlertSignature) {
      lastAlertSignatureRef.current = "";
      return;
    }
    if (!alertsEnabled || alertsSilenced || !alertSoundEnabled || showHero) {
      return;
    }
    if (lastAlertSignatureRef.current === activeAlertSignature) {
      return;
    }
    lastAlertSignatureRef.current = activeAlertSignature;
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const oscillator = ctx.createOscillator();
      const gain = ctx.createGain();
      oscillator.type = "triangle";
      oscillator.frequency.value = 880;
      oscillator.connect(gain);
      gain.connect(ctx.destination);
      gain.gain.setValueAtTime(0.0001, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.12, ctx.currentTime + 0.03);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.28);
      oscillator.start();
      oscillator.stop(ctx.currentTime + 0.3);
      oscillator.onended = () => ctx.close();
    } catch {
      // Ignorar bloqueo de audio por navegador.
    }
  }, [activeAlertSignature, alertsEnabled, alertsSilenced, alertSoundEnabled, showHero]);

  function silenceAlerts(minutes = 15) {
    const until = new Date(Date.now() + minutes * 60 * 1000).toISOString();
    setAlertsSilencedUntil(until);
    setStatus(`Alertas silenciadas por ${minutes} minutos.`);
  }

  function clearAlertSilence() {
    setAlertsSilencedUntil("");
    setStatus("Silenciado de alertas desactivado.");
  }

  async function loadRotationHistory(hostId = selectedHostId) {
    if (!hostId) {
      setRotationHistory([]);
      return;
    }
    try {
      const data = await api.rotationHistory(hostId, 20);
      setRotationHistory(data.items || []);
    } catch {
      setRotationHistory([]);
    }
  }

  async function loadAuditEvents() {
    const hostId = auditHostScope === "selected" ? selectedHostId : "";
    if (auditHostScope === "selected" && !hostId) {
      setAuditEvents([]);
      return;
    }
    setAuditLoading(true);
    try {
      const data = await api.auditEvents({
        host_id: hostId || "",
        event_type: auditTypeFilter === "all" ? "" : auditTypeFilter,
        status: auditStatusFilter === "all" ? "" : auditStatusFilter,
        date_from: auditDateFrom ? `${auditDateFrom}T00:00:00` : "",
        date_to: auditDateTo ? `${auditDateTo}T23:59:59` : "",
        limit: 300,
      });
      setAuditEvents(data.items || []);
    } catch {
      setAuditEvents([]);
    } finally {
      setAuditLoading(false);
    }
  }

  useEffect(() => {
    if (step !== 2 || showHero) return;
    loadAuditEvents();
  }, [
    step,
    showHero,
    selectedHostId,
    auditHostScope,
    auditTypeFilter,
    auditStatusFilter,
    auditDateFrom,
    auditDateTo,
  ]);

  function exportAudit(format = "csv") {
    const rows = auditEvents.map((item) => ({
      timestamp: item.timestamp || "",
      host_name: item.host_name || "",
      host_address: item.host_address || "",
      event_type: item.event_type || "",
      status: item.status || "",
      message: item.message || "",
    }));
    if (!rows.length) {
      setStatus("No hay eventos para exportar.");
      return;
    }

    const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
    if (format === "json") {
      const blob = new Blob([JSON.stringify(rows, null, 2)], { type: "application/json;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `la_huella_auditoria_${stamp}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setStatus("Auditoría exportada en JSON.");
      return;
    }

    const headers = Object.keys(rows[0]);
    const csvEscape = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const lines = [
      headers.join(","),
      ...rows.map((r) => headers.map((h) => csvEscape(r[h])).join(",")),
    ];
    const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `la_huella_auditoria_${stamp}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setStatus("Auditoría exportada en CSV.");
  }

  function toggleAuditDetails(eventKey) {
    setExpandedAuditKey((prev) => (prev === eventKey ? "" : eventKey));
  }

  function parseTemplateTargets(text) {
    return String(text || "")
      .split(/[\s,;]+/)
      .map((x) => x.trim())
      .filter(Boolean);
  }

  function unlockCriticalActions(minutes = 10) {
    if (!criticalGuardEnabled) return;
    const typed = window.prompt("Escribí HABILITAR para desbloquear acciones críticas por 10 minutos.");
    if (typed !== "HABILITAR") {
      setStatus("Desbloqueo cancelado.");
      return;
    }
    const until = new Date(Date.now() + minutes * 60 * 1000).toISOString();
    setCriticalUnlockedUntil(until);
    setStatus(`Acciones críticas habilitadas por ${minutes} minutos.`);
  }

  function lockCriticalActionsNow() {
    setCriticalUnlockedUntil("");
    setStatus("Acciones críticas bloqueadas.");
  }

  function ensureCriticalActionAllowed(actionName, confirmWord) {
    if (!criticalUnlocked) {
      setStatus("Acción crítica bloqueada. Desbloqueá en la barra superior.");
      return false;
    }
    const typed = window.prompt(
      `Acción crítica: ${actionName}. Escribí ${confirmWord} para confirmar.`
    );
    if (typed !== confirmWord) {
      setStatus(`Confirmación inválida para ${actionName}.`);
      return false;
    }
    return true;
  }

  function detectSubnetWithFallback() {
    const candidates = [];
    const pushCandidate = (value) => {
      const v = String(value || "").trim();
      if (!v) return;
      if (!candidates.includes(v)) candidates.push(v);
    };

    const localIp = String(systemInfo?.ip || "").trim();
    if (/^\d+\.\d+\.\d+\.\d+$/.test(localIp)) {
      const parts = localIp.split(".");
      pushCandidate(`${parts[0]}.${parts[1]}.${parts[2]}.0/24`);
    }

    if (hosts.length) {
      const first = String(hosts[0]?.address || "").trim();
      if (/^\d+\.\d+\.\d+\.\d+$/.test(first)) {
        const parts = first.split(".");
        pushCandidate(`${parts[0]}.${parts[1]}.${parts[2]}.0/24`);
      }
    }

    pushCandidate("10.95.25.0/24");
    pushCandidate("192.168.2.0/24");

    const selected = candidates[0] || "10.95.25.0/24";
    setDiscoverSubnet(selected);
    setStatus(`Subred detectada: ${selected}. Fallbacks: ${candidates.slice(1).join(", ") || "-"}`);
  }

  function getTemplateHosts(targets) {
    const wanted = new Set(targets.map((x) => x.toLowerCase()));
    return hosts.filter((host) => wanted.has(String(host.address || "").toLowerCase()));
  }

  function clearTemplateEditor() {
    setSelectedTemplateId("");
    setTemplateName("");
    setTemplateTargetsText("");
  }

  function loadTemplateIntoEditor(templateId) {
    const tpl = opTemplates.find((item) => item.id === templateId);
    if (!tpl) return;
    setSelectedTemplateId(tpl.id);
    setTemplateName(tpl.name || "");
    setTemplateTargetsText((tpl.target_addresses || []).join("\n"));
  }

  function saveOperationTemplate() {
    const name = templateName.trim();
    const targets = parseTemplateTargets(templateTargetsText);
    if (!name) {
      setStatus("Completá el nombre de la plantilla.");
      return;
    }
    if (!targets.length) {
      setStatus("Completá al menos una IP objetivo para la plantilla.");
      return;
    }
    const template = {
      id: selectedTemplateId || `tpl-${Date.now()}`,
      name,
      target_addresses: targets,
      command: command.trim() || "hostname",
      file_path: filePath.trim() || "C:\\",
      remote_path: remotePath.trim() || "C:\\Temp\\lahuella_sync.txt",
      transfer_content: transferContent || "",
      updated_at: new Date().toISOString(),
    };
    setOpTemplates((prev) => {
      const exists = prev.some((item) => item.id === template.id);
      if (!exists) return [template, ...prev];
      return prev.map((item) => (item.id === template.id ? template : item));
    });
    setSelectedTemplateId(template.id);
    setStatus(`Plantilla guardada: ${template.name}.`);
  }

  function deleteOperationTemplate() {
    if (!selectedTemplateId) {
      setStatus("Seleccioná una plantilla para eliminar.");
      return;
    }
    const tpl = opTemplates.find((item) => item.id === selectedTemplateId);
    if (!tpl) return;
    const ok = window.confirm(`¿Eliminar la plantilla "${tpl.name}"?`);
    if (!ok) return;
    setOpTemplates((prev) => prev.filter((item) => item.id !== selectedTemplateId));
    clearTemplateEditor();
    setStatus("Plantilla eliminada.");
  }

  function applyOperationTemplate() {
    const tpl = opTemplates.find((item) => item.id === selectedTemplateId);
    if (!tpl) {
      setStatus("Seleccioná una plantilla para aplicar.");
      return;
    }
    setCommand(tpl.command || "hostname");
    setFilePath(tpl.file_path || "C:\\");
    setRemotePath(tpl.remote_path || "C:\\Temp\\lahuella_sync.txt");
    setTransferContent(tpl.transfer_content || "");
    const resolved = getTemplateHosts(tpl.target_addresses || []);
    if (resolved.length) {
      setSelectedHostId(resolved[0].id);
    }
    setStatus(`Plantilla aplicada: ${tpl.name} (${resolved.length} hosts detectados).`);
  }

  async function runTemplateBatchCommand() {
    const tpl = opTemplates.find((item) => item.id === selectedTemplateId);
    if (!tpl) {
      setStatus("Seleccioná una plantilla para ejecutar por lote.");
      return;
    }
    const targets = tpl.target_addresses || [];
    const matchedHosts = getTemplateHosts(targets);
    if (!matchedHosts.length) {
      setStatus("No hay hosts del sistema que coincidan con las IP de la plantilla.");
      return;
    }
    const confirmText = `Se ejecutará "${tpl.command}" en ${matchedHosts.length} host(s). ¿Continuar?`;
    if (!window.confirm(confirmText)) return;
    if (!ensureCriticalActionAllowed("ejecución por lote", "LOTE")) return;

    setBatchRunning(true);
    const results = [];
    for (const host of matchedHosts) {
      try {
        const data = await api.runCommand(host.id, tpl.command);
        results.push({
          host: host.name,
          address: host.address,
          ok: data?.result?.exit_code === 0,
          text: (data?.result?.stdout || data?.result?.stderr || "").slice(0, 180),
          retried: Boolean(data?._meta?.retried),
        });
      } catch (error) {
        results.push({
          host: host.name,
          address: host.address,
          ok: false,
          text: error.message,
          retried: false,
        });
      }
    }
    setBatchResults(results);
    const okCount = results.filter((x) => x.ok).length;
    setStatus(`Ejecución por lote finalizada: ${okCount}/${results.length} OK.`);
    setBatchRunning(false);
  }

  async function loadHostTopology(hostId = selectedHostId) {
    if (!hostId) {
      setHostTopology(createDefaultTopology());
      return;
    }
    const host = hosts.find((item) => item.id === hostId);
    setTopologyLoading(true);
    try {
      const data = await api.getHostTopology(hostId);
      setHostTopology(data.item || createDefaultTopology(host?.name || ""));
    } catch {
      setHostTopology(createDefaultTopology(host?.name || ""));
    } finally {
      setTopologyLoading(false);
    }
  }

  function updateTopologyField(field, value) {
    setHostTopology((prev) => ({ ...prev, [field]: value }));
  }

  function updateTopologyDevice(index, field, value) {
    setHostTopology((prev) => ({
      ...prev,
      devices: prev.devices.map((device, i) => (i === index ? { ...device, [field]: value } : device)),
    }));
  }

  async function saveHostTopology() {
    if (!selectedHostId) {
      setStatus("Seleccioná un host para guardar su infraestructura.");
      return;
    }
    setLoading(true);
    try {
      await api.updateHostTopology(selectedHostId, hostTopology);
      setStatus("Infraestructura de vía guardada.");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  function exportHostReportCsv() {
    const rows = hosts.map((host) => {
      const c = hostChecks[host.id] || {};
      return {
        name: host.name,
        address: host.address,
        host_type: host.host_type || "windows",
        username: host.username,
        smb_open: c.smb_open ?? "",
        winrm_open: c.winrm_open ?? "",
        auth_success: c.auth_success ?? "",
        ready: c.ready ?? "",
        status: statusText(c),
        auth_error: c.auth_error || ""
      };
    });
    const headers = Object.keys(rows[0] || { name: "", address: "", host_type: "", username: "" });
    const csvEscape = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const lines = [
      headers.join(","),
      ...rows.map((r) => headers.map((h) => csvEscape(r[h])).join(","))
    ];
    const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `la_huella_hosts_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-")}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setStatus("Reporte CSV exportado.");
  }

  async function saveHost(event) {
    event.preventDefault();
    setLoading(true);
    try {
      if (editingHostId) {
        await api.updateHost(editingHostId, hostForm);
        setStatus("Host actualizado");
      } else {
        await api.createHost(hostForm);
        setStatus("Host agregado");
      }
      setHostForm(defaultHostForm);
      setEditingHostId(null);
      setHostModalOpen(false);
      await loadDashboard();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  function editHost(host) {
    setEditingHostId(host.id);
    setHostForm({
      name: host.name,
      address: host.address,
      port: host.port,
      username: host.username,
      password: "",
      host_type: host.host_type ?? "windows",
      winrm_port: host.winrm_port ?? 5985,
      base_path: host.base_path ?? "C:\\",
      restart_command: host.restart_command ?? "shutdown /r /t 5 /f"
    });
    setHostModalOpen(true);
  }

  function openNewHostModal() {
    setEditingHostId(null);
    setHostForm(defaultHostForm);
    setHostModalOpen(true);
  }

  function closeHostModal() {
    setHostModalOpen(false);
    setEditingHostId(null);
    setHostForm(defaultHostForm);
  }

  async function removeHost(hostId) {
    if (!ensureCriticalActionAllowed("borrado de host", "BORRAR")) return;
    setLoading(true);
    try {
      await api.deleteHost(hostId);
      setHostChecks((prev) => {
        const next = { ...prev };
        delete next[hostId];
        return next;
      });
      await loadDashboard();
      setStatus("Host eliminado");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function discoverHosts() {
    setLoading(true);
    try {
      const data = await api.discoverHosts(discoverSubnet, Number(discoverPort));
      setDiscovered(data.items || []);
      setStatus(
        `Descubiertos ${data.count} host(s) con puerto ${discoverPort} abierto.${
          data?._meta?.retried ? " (vía reintento)" : ""
        }`
      );
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function testSelectedCredentials() {
    if (!selectedHostId) return;
    const candidates = credentialCandidates.filter((item) => item.username.trim() && item.password.trim());
    if (!candidates.length) {
      setStatus("Completá usuario y contraseña en al menos una fila.");
      return;
    }
    setLoading(true);
    try {
      const data = await api.testCredentials(selectedHostId, candidates);
      setCredentialResults(data.items || []);
      await quickCheckHost(selectedHostId, true);
      await loadDashboard();
      await loadRotationHistory(selectedHostId);
      setStatus(data.any_success ? "Credenciales válidas detectadas." : "No hubo credenciales válidas.");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setCredentialCandidates((prev) => prev.map((item) => ({ ...item, password: "" })));
      setLoading(false);
    }
  }

  async function rotateSelectedCredentials() {
    if (!ensureCriticalActionAllowed("rotación de credenciales", "ROTAR")) return;
    if (!selectedHostId) return;
    if (!rotateUser.trim() || !rotatePassword.trim()) {
      setStatus("Completá usuario y contraseña nueva para rotar.");
      return;
    }
    setLoading(true);
    try {
      const result = await api.rotateCredentials(
        selectedHostId,
        rotateUser.trim(),
        rotatePassword,
        true,
        true
      );
      if (result.success) {
        setStatus("Rotación OK: credencial actualizada y validada.");
      } else if (result.rolled_back) {
        setStatus(`Rotación revertida: ${result.error}`);
      } else {
        setStatus(`Rotación sin validación OK: ${result.error}`);
      }
      await quickCheckHost(selectedHostId, true);
      await loadDashboard();
      await loadRotationHistory(selectedHostId);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setRotatePassword("");
      setLoading(false);
    }
  }

  async function listRemoteFiles() {
    if (!selectedHostId) return;
    setLoading(true);
    try {
      const data = await api.listHostFiles(selectedHostId, filePath);
      setFileItems(data.items || []);
      setStatus(`Archivos listados en ${filePath}${data?._meta?.retried ? " (vía reintento)" : ""}`);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function executeCommand() {
    if (!selectedHostId || !command.trim()) return;
    setLoading(true);
    try {
      const data = await api.runCommand(selectedHostId, command.trim());
      setStatus(
        `Comando (${data.result.exit_code}): ${data.result.stdout || data.result.stderr}${
          data?._meta?.retried ? " | vía reintento" : ""
        }`
      );
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function restartRemote() {
    if (!ensureCriticalActionAllowed("reinicio remoto", "REINICIAR")) return;
    if (!selectedHostId) return;
    setLoading(true);
    try {
      const data = await api.restartTerminal(selectedHostId);
      setStatus(
        `Reinicio (${data.result.exit_code}): ${data.result.stdout || data.result.stderr}${
          data?._meta?.retried ? " | vía reintento" : ""
        }`
      );
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function uploadText() {
    if (!selectedHostId) return;
    setLoading(true);
    try {
      const data = await api.uploadText(selectedHostId, remotePath, transferContent);
      setStatus(
        `Enviado a ${data.result.remote_path} (${data.result.bytes} bytes).${
          data?._meta?.retried ? " (vía reintento)" : ""
        }`
      );
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function downloadText() {
    if (!selectedHostId) return;
    setLoading(true);
    try {
      const data = await api.downloadText(selectedHostId, remotePath);
      setDownloadContent(data.result.content);
      setStatus(`Descargado desde ${data.result.remote_path}.${data?._meta?.retried ? " (vía reintento)" : ""}`);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function updatePotencia() {
    setLoading(true);
    try {
      await api.updatePotencia(Number(potenciaInput));
      const data = await api.antenna();
      setAntenna(data);
      setStatus(`POTENCIA actualizada a ${potenciaInput}`);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function moveDatFiles() {
    setLoading(true);
    try {
      const data = await api.moveFiles(sourcePath, destinationPath);
      setStatus(data.moved ? `Archivos movidos a ${data.final_folder}` : "No se encontraron .dat.");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  return showHero ? (
    <div className="shell hero-shell">
      <section className="welcome">
        <img src="/logoLH.webp" alt="Logo La Huella" className="welcome-logo" />
          <h1>Sistemas La Huella</h1>
          <p>Centro de operación y gestión remota de hosts</p>
          <div className="row">
          <button onClick={() => setShowHero(false)}>Ir al panel</button>
          </div>
        <div className="secret-links hero-links">
          <a href="https://zeqebellino.com" target="_blank" rel="noreferrer">
            zeqebellino.com
          </a>
          <span>·</span>
          <a href="https://www.github.com/ezebellino" target="_blank" rel="noreferrer">
            github
          </a>
        </div>
      </section>
    </div>
  ) : (
    <div className={`shell ${compactMode ? "compact" : ""} ${cabinaMode ? "cabina" : ""}`}>
      <div className="cabina-sticky-stack">
      <header className="hero">
        <div>
          <button className="title-link" onClick={() => setShowHero(true)}>
            Sistemas La Huella
          </button>
          <p>Panel operativo Windows Server 2019 para red de vías</p>
        </div>
        <div className="chips">
          <span>{systemInfo?.hostname ?? "Servidor local"}</span>
          <span>{systemInfo?.ip ?? "-"}</span>
          <span>Objetivo: {systemInfo?.target_server_ip ?? "10.95.25.10"}</span>
          <span>Subred: {systemInfo?.updated_subnet ?? "10.95.25.0/24"}</span>
        </div>
      </header>

      <section className="kpis">
        <article className="kpi"><span>Total de hosts</span><strong>{summary.total}</strong></article>
        <article className="kpi"><span>Evaluados</span><strong>{summary.tested}</strong></article>
        <article className="kpi"><span>Listos</span><strong>{summary.ready}</strong></article>
        <article className="kpi"><span>Sin Conexión</span><strong>{summary.offline}</strong></article>
        <article className="kpi"><span>Fallo de auth</span><strong>{summary.authFail}</strong></article>
      </section>

      <section className="ops-toolbar">
        <button
          className={operationMode ? "" : "ghost"}
          onClick={() => setOperationMode((prev) => !prev)}
        >
          {operationMode ? "Modo operación: activo" : "Modo operación: inactivo"}
        </button>
        <label className="inline-control">
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
          />
          Autoactualizar
        </label>
        <label className="inline-control">
          <input
            type="checkbox"
            checked={compactMode}
            onChange={(e) => setCompactMode(e.target.checked)}
          />
          Modo compacto
        </label>
        <label className="inline-control">
          <input
            type="checkbox"
            checked={cabinaMode}
            onChange={(e) => setCabinaMode(e.target.checked)}
          />
          Modo cabina
        </label>
        <label className="inline-control">
          <input
            type="checkbox"
            checked={criticalGuardEnabled}
            onChange={(e) => setCriticalGuardEnabled(e.target.checked)}
          />
          Guardia crítica
        </label>
        {criticalGuardEnabled ? (
          <button className="ghost" onClick={() => unlockCriticalActions(10)}>
            {criticalUnlocked ? "Extender desbloqueo" : "Desbloquear 10 min"}
          </button>
        ) : null}
        {criticalGuardEnabled && criticalUnlocked ? (
          <button className="ghost" onClick={lockCriticalActionsNow}>
            Bloquear ahora
          </button>
        ) : null}
        <span className={`hint ${criticalUnlocked ? "state-ok" : "state-warn"}`}>
          {criticalGuardEnabled
            ? criticalUnlocked
              ? "Críticas: habilitadas"
              : "Críticas: bloqueadas"
            : "Críticas: guardia desactivada"}
        </span>
        <label className="inline-control">
          <input
            type="checkbox"
            checked={alertsEnabled}
            onChange={(e) => setAlertsEnabled(e.target.checked)}
          />
          Alertas
        </label>
        <label className="inline-control">
          <input
            type="checkbox"
            checked={alertSoundEnabled}
            onChange={(e) => setAlertSoundEnabled(e.target.checked)}
            disabled={!alertsEnabled}
          />
          Sonido
        </label>
        <input
          type="number"
          min="15"
          max="300"
          value={refreshSeconds}
          onChange={(e) => setRefreshSeconds(e.target.value)}
          className="small-input"
          placeholder="seg"
        />
        <button className="ghost" onClick={monitorNow} disabled={loading}>
          Actualizar estado
        </button>
        <span className="hint">Último monitor: {lastRefreshAt || "-"}</span>
      </section>
      <section className={`alerts-strip ${alerts.length ? "has-alerts" : ""}`}>
        <div className="alerts-summary">
          <strong>Alertas operativas</strong>
          <span>Críticas: {criticalAlerts}</span>
          <span>Advertencias: {warningAlerts}</span>
          {alertsSilenced ? <span className="silenced-pill">Silenciadas</span> : null}
        </div>
        <div className="alerts-actions">
          <button className="ghost" onClick={() => silenceAlerts(15)} disabled={!alerts.length}>
            Silenciar 15 min
          </button>
          <button className="ghost" onClick={clearAlertSilence} disabled={!alertsSilenced}>
            Reactivar
          </button>
        </div>
        <div className="alerts-list">
          {!alertsEnabled ? (
            <span className="hint">Alertas desactivadas por operador.</span>
          ) : !alerts.length ? (
            <span className="hint">Sin alertas activas.</span>
          ) : (
            alerts.slice(0, 8).map((item) => (
              <div key={item.id} className={`alert-item ${item.level}`}>
                <strong>{item.hostName}</strong>
                <span>{item.text}</span>
                <span className="hint">{item.hostAddress}</span>
              </div>
            ))
          )}
        </div>
      </section>
      </div>

      {operationMode ? (
        <main className="grid grid-2">
          <section className="panel">
            <h2>Monitor operativo</h2>
            <div className="group">
              <div className="row">
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Buscar host"
                />
                <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                  <option value="all">Todos</option>
                  <option value="ready">Listos</option>
                  <option value="offline">Sin conexión</option>
                  <option value="auth_fail">Credencial inválida</option>
                </select>
              </div>
            </div>
            <div className="group table-group">
              <div className="host-table-wrap">
              <table className="host-table">
                <thead>
                  <tr>
                    <th>Host</th>
                    <th>SMB</th>
                    <th>WinRM</th>
                    <th>Autenticación</th>
                    <th>Estado</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredHosts.map((host) => {
                    const c = hostChecks[host.id];
                    return (
                      <tr
                        key={`op-${host.id}`}
                        className={selectedHostId === host.id ? "selected-row" : ""}
                        onClick={() => {
                          setSelectedHostId(host.id);
                          setFilePath(host.base_path || "C:\\");
                        }}
                      >
                        <td>
                          <strong>{host.name}</strong>
                          <div className="cell-sub">{host.address}</div>
                        </td>
                        <td><span className={`dot ${c?.smb_open ? "ok" : "bad"}`} /></td>
                        <td><span className={`dot ${c?.winrm_open ? "ok" : "bad"}`} /></td>
                        <td>
                          <span className={`dot ${c?.auth_success === true ? "ok" : c?.auth_success === false ? "bad" : "na"}`} />
                        </td>
                        <td>{statusText(c)}</td>
                        <td>
                          <button
                            className="ghost"
                            onClick={(e) => {
                              e.stopPropagation();
                              quickCheckHost(host.id, true);
                            }}
                          >
                            Probar
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              </div>
            </div>

          </section>

          <section className="panel">
            <h2>Acciones rápidas</h2>
            <p>Seleccionado: {selectedHost ? `${selectedHost.name} (${selectedHost.address})` : "Ninguno"}</p>
            <div className="group">
              <div className="row">
                <input value={command} onChange={(e) => setCommand(e.target.value)} placeholder="hostname" />
                <button onClick={executeCommand} disabled={loading || !selectedHostId}>
                  Ejecutar
                </button>
                <button onClick={restartRemote} disabled={loading || !selectedHostId}>
                  Reiniciar
                </button>
              </div>
            </div>
            <div className="group">
              <div className="row">
                <input value={filePath} onChange={(e) => setFilePath(e.target.value)} placeholder="C:\\Windows" />
                <button onClick={listRemoteFiles} disabled={loading || !selectedHostId}>
                  Ver archivos
                </button>
              </div>
              <div className="list-box">
                {fileItems.slice(0, 15).map((item) => (
                  <div key={`op-file-${item.type}-${item.name}`} className="list-item">
                    <strong>{item.type === "dir" ? "DIR" : "FILE"} | {item.name}</strong>
                    <span>{item.size} bytes - {item.modified}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </main>
      ) : (
        <>
          <div className="steps">
            {steps.map((item) => (
              <button
                key={item.id}
                className={`step-chip ${step === item.id ? "active" : ""}`}
                onClick={() => setStep(item.id)}
              >
                {item.id}. {item.title}
              </button>
            ))}
          </div>

      {step === 1 && (
        <main className="grid grid-2">
          <section className="panel">
            <h2>Diagnóstico de Red</h2>
            <div className="group">
              <h3>Escaneo de red</h3>
              <div className="row">
                <input value={discoverSubnet} onChange={(e) => setDiscoverSubnet(e.target.value)} />
                <input
                  type="number"
                  value={discoverPort}
                  onChange={(e) => setDiscoverPort(e.target.value)}
                  placeholder="Puerto"
                />
                <button className="ghost" onClick={detectSubnetWithFallback} disabled={loading}>
                  Detectar subred
                </button>
                <button onClick={discoverHosts} disabled={loading}>
                  Escanear
                </button>
              </div>
              <div className="list-box">
                {discovered.map((item) => (
                  <div key={item.address} className="list-item">
                    <strong>{item.address}</strong>
                    <span>{item.already_saved ? "ya guardado" : "nuevo"}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="group">
              <h3>Operación local</h3>
              <div className="row">
                <input
                  type="number"
                  min="0"
                  max="30"
                  value={potenciaInput}
                  onChange={(e) => setPotenciaInput(e.target.value)}
                  placeholder="Potencia"
                />
                <button onClick={updatePotencia} disabled={loading}>
                  Actualizar
                </button>
              </div>
              <p>Host remoto: {antenna?.remote_host ?? "-"}</p>
              <input value={sourcePath} onChange={(e) => setSourcePath(e.target.value)} />
              <input
                value={destinationPath}
                onChange={(e) => setDestinationPath(e.target.value)}
                placeholder="Destino .dat"
              />
              <button onClick={moveDatFiles} disabled={loading || !destinationPath.trim()}>
                Mover .dat
              </button>
            </div>
          </section>

          <section className="panel">
            <h2>Estado de Tags</h2>
            <div className="group">
              {tags.map((tag) => (
                <div key={tag.nombre} className="list-item">
                  <strong>{tag.nombre}</strong>
                  <span>
                    {tag.tamano} MB - {tag.ultima_mod}
                  </span>
                </div>
              ))}
            </div>
          </section>
        </main>
      )}

      {step === 2 && (
        <main className="grid grid-2">
          <section className="panel">
            <h2>Hosts y credenciales</h2>
            <div className="group">
              <div className="row">
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Buscar host por nombre/IP/usuario"
                />
                <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                  <option value="all">Todos</option>
                  <option value="ready">Listos</option>
                  <option value="offline">Sin conexión</option>
                  <option value="auth_fail">Credencial inválida</option>
                </select>
                <button onClick={quickCheckAll} disabled={loading || !hosts.length}>
                  Test rápido
                </button>
                <button className="ghost" onClick={exportHostReportCsv} disabled={!hosts.length}>
                  Exportar CSV
                </button>
              </div>
            </div>
            <div className="group table-group">
              <div className="host-table-wrap">
              <table className="host-table">
                <thead>
                  <tr>
                    <th>Host</th>
                    <th>SMB</th>
                    <th>WinRM</th>
                    <th>Autenticación</th>
                    <th>Estado</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredHosts.map((host) => {
                    const c = hostChecks[host.id];
                    return (
                      <tr
                        key={host.id}
                        className={selectedHostId === host.id ? "selected-row" : ""}
                        onClick={() => {
                          setSelectedHostId(host.id);
                          setFilePath(host.base_path || "C:\\");
                          setCredentialResults([]);
                          loadRotationHistory(host.id);
                        }}
                      >
                        <td>
                          <strong>{host.name}</strong>
                          <div className="cell-sub">{host.address}</div>
                        </td>
                        <td><span className={`dot ${c?.smb_open ? "ok" : "bad"}`} /></td>
                        <td><span className={`dot ${c?.winrm_open ? "ok" : "bad"}`} /></td>
                        <td>
                          <span className={`dot ${c?.auth_success === true ? "ok" : c?.auth_success === false ? "bad" : "na"}`} />
                        </td>
                        <td>{statusText(c)}</td>
                        <td>
                          <button
                            className="ghost"
                            onClick={(e) => {
                              e.stopPropagation();
                              quickCheckHost(host.id, true);
                            }}
                          >
                            Probar
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              </div>
            </div>

            <div className="group">
              <div className="row">
                <h3 style={{ margin: 0 }}>Historial y auditoría</h3>
                <button className="ghost" onClick={loadAuditEvents} disabled={auditLoading}>
                  Actualizar eventos
                </button>
                <button className="ghost" onClick={() => exportAudit("csv")} disabled={!auditEvents.length}>
                  Exportar CSV
                </button>
                <button className="ghost" onClick={() => exportAudit("json")} disabled={!auditEvents.length}>
                  Exportar JSON
                </button>
              </div>
              <div className="row">
                <select value={auditHostScope} onChange={(e) => setAuditHostScope(e.target.value)}>
                  <option value="selected">Host seleccionado</option>
                  <option value="all">Todos los hosts</option>
                </select>
                <select value={auditTypeFilter} onChange={(e) => setAuditTypeFilter(e.target.value)}>
                  <option value="all">Tipo de evento: todos</option>
                  <option value="host_command">Comando remoto</option>
                  <option value="host_terminal_restart">Reinicio terminal</option>
                  <option value="host_files_list">Listado de archivos</option>
                  <option value="host_upload_text">Envío de archivo/texto</option>
                  <option value="host_download_text">Descarga de archivo/texto</option>
                  <option value="host_credentials_test">Test credenciales</option>
                  <option value="host_credentials_rotate">Rotación credenciales</option>
                  <option value="host_create">Alta de host</option>
                  <option value="host_update">Edición de host</option>
                  <option value="host_delete">Baja de host</option>
                  <option value="hosts_discover">Escaneo de red</option>
                  <option value="topology_update">Edición de topología</option>
                </select>
                <select value={auditStatusFilter} onChange={(e) => setAuditStatusFilter(e.target.value)}>
                  <option value="all">Estado: todos</option>
                  <option value="ok">OK</option>
                  <option value="warning">Advertencia</option>
                  <option value="error">Error</option>
                </select>
              </div>
              <div className="row">
                <input type="date" value={auditDateFrom} onChange={(e) => setAuditDateFrom(e.target.value)} />
                <input type="date" value={auditDateTo} onChange={(e) => setAuditDateTo(e.target.value)} />
              </div>
              <div className="list-box audit-list">
                {auditLoading ? <span className="hint">Cargando auditoría...</span> : null}
                {!auditLoading && !auditEvents.length ? (
                  <span className="hint">Sin eventos para el filtro seleccionado.</span>
                ) : null}
                {!auditLoading &&
                  auditEvents.map((event, idx) => {
                    const eventKey = `${event.timestamp || "ts"}-${event.event_type || "type"}-${idx}`;
                    const expanded = expandedAuditKey === eventKey;
                    return (
                      <div key={eventKey} className={`list-item audit-item ${event.status || "ok"}`}>
                        <button
                          className="audit-item-head"
                          onClick={() => toggleAuditDetails(eventKey)}
                          type="button"
                        >
                          <strong>
                            {event.event_type || "evento"} | {event.status || "ok"} |{" "}
                            {event.host_name || "host local"}
                          </strong>
                          <span>{expanded ? "Ocultar" : "Ver detalle"}</span>
                        </button>
                        <span>
                          {event.timestamp || "-"} - {event.message || "-"}
                        </span>
                        {event.host_address ? <span className="hint">{event.host_address}</span> : null}
                        {expanded && event.details ? (
                          <pre className="audit-details">{JSON.stringify(event.details, null, 2)}</pre>
                        ) : null}
                      </div>
                    );
                  })}
              </div>
            </div>
          </section>

          <section className="panel">
            <h2>Gestión de host</h2>
            <div className="group">
              <div className="row">
                <button type="button" onClick={openNewHostModal}>
                  Agregar nuevo host
                </button>
                <button
                  type="button"
                  className="ghost"
                  onClick={() => selectedHost && editHost(selectedHost)}
                  disabled={!selectedHost}
                >
                  Editar host seleccionado
                </button>
                <button
                  type="button"
                  className="danger"
                  onClick={() => selectedHost && removeHost(selectedHost.id)}
                  disabled={!selectedHost}
                >
                  Borrar host seleccionado
                </button>
              </div>
              <span className="hint">
                {selectedHost
                  ? `Seleccionado: ${selectedHost.name} (${selectedHost.address})`
                  : "Seleccioná un host de la tabla para editar o borrar."}
              </span>
            </div>

            <div className="group">
              <h3>Chequeo de credenciales</h3>
              {credentialCandidates.map((item, idx) => (
                <div className="row" key={`cred-${idx}`}>
                  <input
                    value={item.username}
                    onChange={(e) =>
                      setCredentialCandidates((prev) =>
                        prev.map((row, i) => (i === idx ? { ...row, username: e.target.value } : row))
                      )
                    }
                    placeholder="Usuario"
                  />
                  <input
                    type="password"
                    value={item.password}
                    onChange={(e) =>
                      setCredentialCandidates((prev) =>
                        prev.map((row, i) => (i === idx ? { ...row, password: e.target.value } : row))
                      )
                    }
                    placeholder="Contraseña"
                  />
                </div>
              ))}
              <button onClick={testSelectedCredentials} disabled={loading || !selectedHostId}>
                Validar credenciales
              </button>
              <div className="list-box">
                {credentialResults.map((item) => (
                  <div key={`${item.username}-res`} className="list-item">
                    <strong>{item.username} - {item.success ? "OK" : "FAIL"}</strong>
                    <span>{item.error || "Autenticación correcta"}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="group">
              <h3>Rotación de credenciales (con verificación)</h3>
              <div className="row">
                <input
                  value={rotateUser}
                  onChange={(e) => setRotateUser(e.target.value)}
                  placeholder="Usuario nuevo"
                />
                <input
                  type="password"
                  value={rotatePassword}
                  onChange={(e) => setRotatePassword(e.target.value)}
                  placeholder="Contraseña nueva"
                />
              </div>
              <button onClick={rotateSelectedCredentials} disabled={loading || !selectedHostId}>
                Rotar y verificar
              </button>
              <span className="hint">
                Si falla autenticación, el sistema revierte automáticamente a la credencial anterior.
              </span>
            </div>

            <div className="group">
              <div className="row">
                <h3 style={{ margin: 0 }}>Historial de rotaciones</h3>
                <button className="ghost" onClick={() => loadRotationHistory()} disabled={loading || !selectedHostId}>
                  Actualizar historial
                </button>
              </div>
              <div className="list-box">
                {rotationHistory.map((item, idx) => (
                  <div key={`rot-${idx}`} className="list-item">
                    <strong>
                      {item.success ? "OK" : "FAIL"} | {item.new_username} |{" "}
                      {item.rolled_back ? "rollback" : "sin rollback"}
                    </strong>
                    <span>
                      {item.timestamp} - {item.error || "sin error"}
                    </span>
                  </div>
                ))}
                {!rotationHistory.length && <span className="hint">Sin historial para este host.</span>}
              </div>
            </div>

            <div className="group">
              <div className="row">
                <h3 style={{ margin: 0 }}>Infraestructura de vía</h3>
                <button className="ghost" onClick={() => loadHostTopology()} disabled={loading || !selectedHostId}>
                  Recargar mapa
                </button>
              </div>
              <span className="hint">
                Visualizá y documentá puntos del switch por host: antena, PC, impresora, cámara de vigilancia y OCR.
              </span>
              {!selectedHostId ? (
                <span className="hint">Seleccioná un host para cargar su mapa.</span>
              ) : (
                <>
                  <div className="row">
                    <input
                      value={hostTopology.switch_name}
                      onChange={(e) => updateTopologyField("switch_name", e.target.value)}
                      placeholder="Nombre del switch"
                    />
                    <input
                      value={hostTopology.switch_ip}
                      onChange={(e) => updateTopologyField("switch_ip", e.target.value)}
                      placeholder="IP del switch"
                    />
                  </div>
                  <div className="row">
                    <input
                      value={hostTopology.switch_model}
                      onChange={(e) => updateTopologyField("switch_model", e.target.value)}
                      placeholder="Modelo (ej: TP-Link, Cisco, Mikrotik)"
                    />
                    <input
                      value={hostTopology.switch_location}
                      onChange={(e) => updateTopologyField("switch_location", e.target.value)}
                      placeholder="Ubicación física"
                    />
                  </div>
                  <textarea
                    rows={2}
                    value={hostTopology.notes}
                    onChange={(e) => updateTopologyField("notes", e.target.value)}
                    placeholder="Notas generales de infraestructura"
                  />
                  <div className="topology-grid">
                    {hostTopology.devices?.map((device, idx) => (
                      <div className="topology-row" key={device.key}>
                        <div className="topology-label">{device.label}</div>
                        <input
                          value={device.port || ""}
                          onChange={(e) => updateTopologyDevice(idx, "port", e.target.value)}
                          placeholder="1 / Gi0/1"
                        />
                        <input
                          value={device.ip || ""}
                          onChange={(e) => updateTopologyDevice(idx, "ip", e.target.value)}
                          placeholder="10.95.25.x"
                        />
                        <input
                          value={device.hostname || ""}
                          onChange={(e) => updateTopologyDevice(idx, "hostname", e.target.value)}
                          placeholder="Nombre visible"
                        />
                        <select
                          value={device.status || "unknown"}
                          onChange={(e) => updateTopologyDevice(idx, "status", e.target.value)}
                        >
                          <option value="ok">Operativo</option>
                          <option value="intermittent">Intermitente</option>
                          <option value="offline">Sin enlace</option>
                          <option value="unknown">Sin validar</option>
                        </select>
                        <input
                          value={device.notes || ""}
                          onChange={(e) => updateTopologyDevice(idx, "notes", e.target.value)}
                          placeholder="Obs."
                        />
                      </div>
                    ))}
                  </div>
                  <div className="row">
                    <button onClick={saveHostTopology} disabled={loading || topologyLoading}>
                      Guardar mapa de infraestructura
                    </button>
                    <span className="hint">{topologyLoading ? "Cargando topología..." : " "}</span>
                  </div>
                </>
              )}
            </div>

          </section>
        </main>
      )}

      {step === 3 && (
        <main className="grid grid-2">
          <section className="panel">
            <h2>Acciones del host</h2>
            <p>Seleccionado: {selectedHost ? `${selectedHost.name} (${selectedHost.address})` : "Ninguno"}</p>
            <div className="group">
              <h3>Explorador de archivos</h3>
              <div className="row">
                <input value={filePath} onChange={(e) => setFilePath(e.target.value)} placeholder="C:\\Windows" />
                <button onClick={listRemoteFiles} disabled={loading || !selectedHostId}>
                  Ver archivos
                </button>
              </div>
              <div className="list-box">
                {fileItems.map((item) => (
                  <div key={`${item.type}-${item.name}`} className="list-item">
                    <strong>{item.type === "dir" ? "DIR" : "FILE"} | {item.name}</strong>
                    <span>{item.size} bytes - {item.modified}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="panel">
            <h2>Terminal y Transferencia</h2>
            <div className="group">
              <h3>Plantillas operativas por grupo</h3>
              <div className="row">
                <select
                  value={selectedTemplateId}
                  onChange={(e) => loadTemplateIntoEditor(e.target.value)}
                >
                  <option value="">Seleccionar plantilla</option>
                  {opTemplates.map((tpl) => (
                    <option key={tpl.id} value={tpl.id}>
                      {tpl.name}
                    </option>
                  ))}
                </select>
                <button className="ghost" onClick={clearTemplateEditor}>
                  Nueva
                </button>
                <button className="danger" onClick={deleteOperationTemplate} disabled={!selectedTemplateId}>
                  Eliminar
                </button>
              </div>
              <input
                value={templateName}
                onChange={(e) => setTemplateName(e.target.value)}
                placeholder="Nombre de plantilla (ej: Vías 51-55)"
              />
              <textarea
                rows={3}
                value={templateTargetsText}
                onChange={(e) => setTemplateTargetsText(e.target.value)}
                placeholder="IPs objetivo (una por línea o separadas por coma)"
              />
              <div className="row">
                <button onClick={saveOperationTemplate}>Guardar plantilla</button>
                <button className="ghost" onClick={applyOperationTemplate} disabled={!selectedTemplateId}>
                  Aplicar al panel
                </button>
                <button
                  className="ghost"
                  onClick={runTemplateBatchCommand}
                  disabled={!selectedTemplateId || batchRunning}
                >
                  {batchRunning ? "Ejecutando lote..." : "Ejecutar por lote"}
                </button>
              </div>
              <div className="list-box">
                {batchResults.map((item, idx) => (
                  <div key={`batch-${idx}`} className="list-item">
                    <strong>
                      {item.ok ? "OK" : "FAIL"} | {item.host} ({item.address})
                      {item.retried ? " | reintento" : ""}
                    </strong>
                    <span>{item.text || "-"}</span>
                  </div>
                ))}
                {!batchResults.length && (
                  <span className="hint">
                    Guardá una plantilla con IPs de vías y ejecutá acciones por lote con confirmación.
                  </span>
                )}
              </div>
            </div>
            <div className="group">
              <h3>Comandos</h3>
              <div className="row">
                <input value={command} onChange={(e) => setCommand(e.target.value)} placeholder="hostname" />
                <button onClick={executeCommand} disabled={loading || !selectedHostId}>
                  Ejecutar
                </button>
                <button onClick={restartRemote} disabled={loading || !selectedHostId}>
                  Reiniciar
                </button>
              </div>
            </div>
            <div className="group">
              <h3>Transferencia</h3>
              <input value={remotePath} onChange={(e) => setRemotePath(e.target.value)} placeholder="C:\\Temp\\archivo.txt" />
              <textarea rows={5} value={transferContent} onChange={(e) => setTransferContent(e.target.value)} />
              <div className="row">
                <button onClick={uploadText} disabled={loading || !selectedHostId}>Enviar</button>
                <button onClick={downloadText} disabled={loading || !selectedHostId}>Descargar</button>
              </div>
              <textarea rows={5} value={downloadContent} readOnly placeholder="Contenido recibido" />
            </div>
          </section>
        </main>
      )}
        </>
      )}

      {hostModalOpen && (
        <div className="modal-backdrop" onClick={closeHostModal}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingHostId ? "Editar host" : "Agregar nuevo host"}</h3>
              <button type="button" className="ghost" onClick={closeHostModal}>
                Cerrar
              </button>
            </div>
            <form className="modal-body" onSubmit={saveHost}>
              <input
                value={hostForm.name}
                onChange={(e) => setHostForm({ ...hostForm, name: e.target.value })}
                placeholder="Nombre"
                required
              />
              <input
                value={hostForm.address}
                onChange={(e) => setHostForm({ ...hostForm, address: e.target.value })}
                placeholder="IP o DNS"
                required
              />
              <div className="row">
                <input
                  type="number"
                  value={hostForm.port}
                  onChange={(e) => setHostForm({ ...hostForm, port: Number(e.target.value) })}
                  placeholder="Puerto SMB"
                />
                <input
                  value={hostForm.username}
                  onChange={(e) => setHostForm({ ...hostForm, username: e.target.value })}
                  placeholder="Usuario"
                />
              </div>
              <div className="row">
                <select
                  value={hostForm.host_type}
                  onChange={(e) => setHostForm({ ...hostForm, host_type: e.target.value })}
                >
                  <option value="windows">Windows Server</option>
                  <option value="linux">Linux</option>
                </select>
                <input
                  type="number"
                  value={hostForm.winrm_port}
                  onChange={(e) => setHostForm({ ...hostForm, winrm_port: Number(e.target.value) })}
                  placeholder="Puerto WinRM"
                />
              </div>
              <input
                type="password"
                value={hostForm.password}
                onChange={(e) => setHostForm({ ...hostForm, password: e.target.value })}
                placeholder={editingHostId ? "Contraseña (dejar vacío para mantener)" : "Contraseña"}
              />
              <input
                value={hostForm.base_path}
                onChange={(e) => setHostForm({ ...hostForm, base_path: e.target.value })}
                placeholder="Ruta base"
              />
              <input
                value={hostForm.restart_command}
                onChange={(e) => setHostForm({ ...hostForm, restart_command: e.target.value })}
                placeholder="Comando de reinicio"
              />
              <div className="row">
                <button type="submit" disabled={loading}>
                  {editingHostId ? "Guardar cambios" : "Agregar host"}
                </button>
                <button type="button" className="ghost" onClick={closeHostModal}>
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <footer className="status">
        <button onClick={loadDashboard} disabled={loading}>Actualizar panel</button>
        <pre>{status}</pre>
      </footer>
    </div>
  );
}



