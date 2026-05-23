// src/App.jsx - EXTENDED WITH IMPACT ANALYSIS MODAL
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

// ============================================
// CONFIGURATION
// ============================================
const API_BASE = 'http://localhost:5000';

const THREAT_TYPES = [
  { value: 'brute_force', label: 'Brute Force', icon: '🔓', description: 'Multiple failed login attempts' },
  { value: 'data_exfiltration', label: 'Data Exfiltration', icon: '📤', description: 'High data transfer detected' },
  { value: 'impossible_travel', label: 'Impossible Travel', icon: '✈️', description: 'Login from distant locations' },
  { value: 'suspicious_behavior', label: 'Suspicious Behavior', icon: '🕵️', description: 'Odd time activity' },
  { value: 'admin_misuse', label: 'Admin Misuse', icon: '👑', description: 'Excessive admin actions' },
  { value: 'background_activity', label: 'Background Activity', icon: '🤖', description: 'Repeated automated tasks' },
];

// ============================================
// HELPER FUNCTIONS
// ============================================

function getScoreColor(score) {
  if (score >= 0.7) return 'bg-red-500/20 text-red-400 border-red-500/30';
  if (score >= 0.4) return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
  return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
}

function getThreatBadgeColor(threatType) {
  const colors = {
    brute_force: 'bg-red-500/20 text-red-400 border-red-500/30',
    data_exfiltration: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    impossible_travel: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    suspicious_behavior: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    admin_misuse: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
    background_activity: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  };
  return colors[threatType] || 'bg-slate-500/20 text-slate-400 border-slate-500/30';
}

function formatThreatType(type) {
  return type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

// ============================================
// SUB-COMPONENTS
// ============================================

function StatusNotification({ notification, onClose }) {
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(onClose, 4000);
      return () => clearTimeout(timer);
    }
  }, [notification, onClose]);

  if (!notification) return null;

  const bgColor = notification.type === 'error'
    ? 'bg-red-500/20 border-red-500/50 text-red-300'
    : 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300';

  return (
    <div className={`fixed top-4 right-4 z-50 px-6 py-3 rounded-lg border ${bgColor} backdrop-blur-sm shadow-2xl animate-slide-up`}>
      <div className="flex items-center gap-3">
        <span>{notification.type === 'error' ? '❌' : '✅'}</span>
        <span className="font-medium">{notification.message}</span>
        <button onClick={onClose} className="ml-2 hover:opacity-70 transition-opacity">✕</button>
      </div>
    </div>
  );
}

function StatsCard({ icon, label, value, colorClass }) {
  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 hover:bg-slate-800/70 transition-all duration-300 hover:border-slate-600/50 hover:shadow-lg hover:shadow-slate-900/50">
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <p className="text-slate-400 text-sm font-medium">{label}</p>
          <p className={`text-2xl font-bold ${colorClass || 'text-white'}`}>{value}</p>
        </div>
      </div>
    </div>
  );
}

function AttackDropdown({ isOpen, onToggle, onSelect, isLoading }) {
  return (
    <div className="relative">
      <button
        onClick={onToggle}
        disabled={isLoading}
        className="flex items-center gap-2 px-5 py-2.5 bg-red-600 hover:bg-red-700 disabled:bg-red-800 disabled:opacity-50 text-white font-semibold rounded-lg transition-all duration-200 shadow-lg shadow-red-900/30 hover:shadow-red-900/50"
      >
        <span>⚔️</span>
        <span>Simulate Attack</span>
        <svg className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full mt-2 left-0 w-72 bg-slate-800 border border-slate-700 rounded-xl shadow-2xl shadow-black/50 z-40 overflow-hidden animate-slide-up">
          <div className="p-2">
            <p className="px-3 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Select Attack Type
            </p>
            {THREAT_TYPES.map((threat) => (
              <button
                key={threat.value}
                onClick={() => onSelect(threat.value)}
                className="w-full flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-slate-700/70 transition-colors duration-150 text-left group"
              >
                <span className="text-xl group-hover:scale-110 transition-transform">
                  {threat.icon}
                </span>
                <div>
                  <p className="text-white font-medium text-sm">{threat.label}</p>
                  <p className="text-slate-400 text-xs">{threat.description}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="relative">
        <div className="w-16 h-16 border-4 border-slate-700 rounded-full"></div>
        <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin absolute top-0 left-0"></div>
      </div>
      <p className="text-slate-400 mt-6 font-medium">Analyzing threats...</p>
      <p className="text-slate-500 text-sm mt-1">Scanning log data for anomalies</p>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 animate-fade-in">
      <div className="text-6xl mb-4">🛡️</div>
      <h3 className="text-xl font-bold text-slate-300 mb-2">No Threats Detected</h3>
      <p className="text-slate-500 text-center max-w-md">
        All systems are running normally. Simulate an attack to see the detection system in action.
      </p>
      <div className="flex items-center gap-2 mt-6 text-slate-600 text-sm">
        <span>💡</span>
        <span>Click "Simulate Attack" to generate threat scenarios</span>
      </div>
    </div>
  );
}

// ============================================
// IMPACT ANALYSIS COMPONENTS (NEW - INLINE)
// ============================================

const severityColors = {
  low: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  critical: 'bg-red-500/20 text-red-400 border-red-500/30',
};

const impactLevelColors = {
  low: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  critical: 'bg-red-500/20 text-red-400 border-red-500/30',
};

function AttackTimeline({ timeline }) {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="text-slate-500 text-center py-8">
        No timeline data available
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-slate-700"></div>
      <div className="space-y-6">
        {timeline.map((stage, index) => (
          <div key={index} className="flex items-start gap-4 relative">
            <div className="relative z-10 w-12 h-12 rounded-full bg-slate-800 border-2 border-slate-700 
                          flex items-center justify-center text-sm font-bold text-white flex-shrink-0">
              {stage.stage}
            </div>
            <div className="flex-1 bg-slate-800/50 rounded-lg p-4 border border-slate-700/50 
                          hover:bg-slate-800/70 transition-all duration-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-500">
                  {stage.time}
                </span>
                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs 
                                font-semibold border ${severityColors[stage.severity]}`}>
                  {stage.severity.toUpperCase()}
                </span>
              </div>
              <p className="text-white font-medium mb-2">
                {stage.description}
              </p>
              <p className="text-slate-400 text-sm">
                {stage.action}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ImpactSummary({ impact }) {
  if (!impact) {
    return <div className="text-slate-500">No impact data available</div>;
  }

  const {
    impact_level,
    impact_description,
    time_to_critical,
    affected_assets,
    business_impact,
    recovery_time_estimate,
    required_actions,
  } = impact;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-center">
        <span className={`inline-flex items-center gap-2 px-6 py-3 rounded-full text-lg 
                        font-bold border ${impactLevelColors[impact_level]}`}>
          Impact Level: {impact_level.toUpperCase()}
        </span>
      </div>

      <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
        <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-2">
          Impact Description
        </h4>
        <p className="text-slate-300 leading-relaxed">
          {impact_description}
        </p>
      </div>

      <div className="flex items-center gap-3">
        <span className="text-slate-500 font-medium">Time to Critical:</span>
        <span className={`inline-flex px-3 py-1 rounded-md text-sm font-bold border 
                        ${impactLevelColors[impact_level]}`}>
          {time_to_critical}
        </span>
      </div>

      <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
        <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-3">
          Affected Assets
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {affected_assets?.map((asset, idx) => (
            <div key={idx} className="flex items-center gap-2 text-sm text-slate-300">
              <span className="text-red-400">•</span>
              {asset}
            </div>
          )) || <span className="text-slate-500">No assets listed</span>}
        </div>
      </div>

      <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
        <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-3">
          Business Impact
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-slate-500 mb-1">Financial</p>
            <p className="text-sm text-slate-300">{business_impact?.financial || 'N/A'}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">Operational</p>
            <p className="text-sm text-slate-300">{business_impact?.operational || 'N/A'}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">Reputational</p>
            <p className="text-sm text-slate-300">{business_impact?.reputational || 'N/A'}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-1">Compliance</p>
            <p className="text-sm text-slate-300">{business_impact?.compliance || 'N/A'}</p>
          </div>
        </div>
      </div>

      <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
        <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-2">
          Recovery Time Estimate
        </h4>
        <p className="text-slate-300">{recovery_time_estimate}</p>
      </div>

      <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/50">
        <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-3">
          Required Actions
        </h4>
        <div className="space-y-2">
          {required_actions?.map((action, idx) => (
            <div key={idx} className="flex items-start gap-3 text-sm">
              <span className="text-cyan-400 mt-1">➤</span>
              <span className="text-slate-300">{action}</span>
            </div>
          )) || <span className="text-slate-500">No actions listed</span>}
        </div>
      </div>
    </div>
  );
}

// ============================================
// ALERTS TABLE COMPONENT
// ============================================

function AlertsTable({ alerts, expandedRow, onToggleRow, onOpenImpact }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-slate-700/50">
            {['', 'User', 'Action', 'Threat Type', 'Anomaly Score', 'Top Factor', 'Recommendation'].map((header) => (
              <th key={header} className="px-5 py-4 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">
                {header}
              </th>
            ))}
          </tr>
        </thead>

        <tbody className="divide-y divide-slate-700/30">
          {alerts.map((alert, index) => (
            <React.Fragment key={index}>
              <tr
                onClick={() => onToggleRow(index)}
                className="hover:bg-slate-800/50 transition-colors duration-150 cursor-pointer group"
              >
                <td className="px-5 py-4">
                  <svg className={`w-4 h-4 text-slate-500 transition-transform duration-200 ${expandedRow === index ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </td>

                <td className="px-5 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-sm font-bold text-cyan-400">
                      {(alert.log?.user || '?')[0].toUpperCase()}
                    </div>
                    <span className="text-white font-medium">{alert.log?.user || 'N/A'}</span>
                  </div>
                </td>

                <td className="px-5 py-4">
                  <code className="text-sm text-slate-300 bg-slate-800 px-2 py-1 rounded font-mono">
                    {alert.log?.action || 'N/A'}
                  </code>
                </td>

                <td className="px-5 py-4">
                  <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${getThreatBadgeColor(alert.threat_type)}`}>
                    {THREAT_TYPES.find(t => t.value === alert.threat_type)?.icon || '⚠️'}
                    {formatThreatType(alert.threat_type)}
                  </span>
                </td>

                <td className="px-5 py-4">
                  <div className="flex items-center gap-3">
                    <span className={`inline-flex px-2.5 py-1 rounded-md text-xs font-bold border ${getScoreColor(alert.anomaly_score)}`}>
                      {alert.anomaly_score?.toFixed(2) || '0.00'}
                    </span>
                    <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          alert.anomaly_score >= 0.7 ? 'bg-red-500' :
                          alert.anomaly_score >= 0.4 ? 'bg-amber-500' : 'bg-emerald-500'
                        }`}
                        style={{ width: `${(alert.anomaly_score || 0) * 100}%` }}
                      />
                    </div>
                  </div>
                </td>

                <td className="px-5 py-4">
                  <span className="text-sm text-slate-300">
                    {alert.explanation?.top_factors?.[0]?.factor || alert.reason?.slice(0, 50) || 'N/A'}
                  </span>
                </td>

                <td className="px-5 py-4 max-w-xs">
                  <span className="text-sm text-slate-400 line-clamp-2">
                    {alert.recommendation || 'N/A'}
                  </span>
                </td>
              </tr>

              {expandedRow === index && (
                <tr className="animate-fade-in">
                  <td colSpan={7} className="px-5 py-0">
                    <div className="bg-slate-800/80 rounded-xl p-6 mb-4 mt-1 border border-slate-700/50">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-4">
                          <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full"></span>
                            Alert Details
                          </h4>
                          <div className="space-y-3">
                            <div>
                              <p className="text-xs text-slate-500 mb-1">Full Reason</p>
                              <p className="text-sm text-slate-300 bg-slate-900/50 p-3 rounded-lg">
                                {alert.reason || 'No reason provided'}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-slate-500 mb-1">Full Recommendation</p>
                              <p className="text-sm text-emerald-300/80 bg-slate-900/50 p-3 rounded-lg">
                                {alert.recommendation || 'No recommendation'}
                              </p>
                            </div>
                          </div>
                        </div>

                        <div className="space-y-4">
                          <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                            <span className="w-1.5 h-1.5 bg-purple-400 rounded-full"></span>
                            Log Metadata
                          </h4>
                          <div className="grid grid-cols-2 gap-3">
                            {[
                              { label: 'Timestamp', value: alert.log?.timestamp },
                              { label: 'IP Address', value: alert.log?.ip },
                              { label: 'Location', value: alert.log?.location },
                              { label: 'Status', value: alert.log?.status },
                              { label: 'Data Transferred', value: alert.log?.data_transferred_mb ? `${alert.log.data_transferred_mb} MB` : null },
                              { label: 'Threat Label', value: alert.log?.threat_type },
                            ].map(({ label, value }) => (
                              value && (
                                <div key={label} className="bg-slate-900/50 p-3 rounded-lg">
                                  <p className="text-xs text-slate-500 mb-1">{label}</p>
                                  <p className="text-sm text-white font-medium">{value}</p>
                                </div>
                              )
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* IMPACT ANALYSIS BUTTON (NEW) */}
                      <div className="mt-6 pt-6 border-t border-slate-800">
                        <div className="flex justify-end">
                          <button
                            onClick={() => onOpenImpact(alert)}
                            className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 
                                     hover:from-purple-700 hover:to-blue-700 text-white font-semibold rounded-lg 
                                     transition-all duration-200 shadow-lg"
                          >
                            <span>📊</span>
                            <span>View Full Impact Analysis</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ============================================
// MAIN APP COMPONENT
// ============================================

function App() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [expandedRow, setExpandedRow] = useState(null);
  const [notification, setNotification] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [stats, setStats] = useState({
  totalLogs: 0,
  totalThreats: 0,
  highSeverity: 0,
  mediumSeverity: 0,
  lowSeverity: 0,
  threatBreakdown: {},
});
  
  // NEW: Impact Analysis Modal State
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [showImpactModal, setShowImpactModal] = useState(false);

  const showNotification = useCallback((message, type = 'success') => {
    setNotification({ message, type });
  }, []);

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/alerts`);
      const data = response.data;

      setAlerts(data.alerts || []);
      setLastRefresh(new Date().toLocaleTimeString());

    const alerts = data.alerts || [];
const highSev = alerts.filter(a => a.anomaly_score >= 0.82).length;
const medSev  = alerts.filter(a => a.anomaly_score >= 0.68 && a.anomaly_score < 0.82).length;
const lowSev  = alerts.filter(a => a.anomaly_score < 0.68).length;
setStats({
  totalLogs: data.total_logs_analyzed || 0,
  totalThreats: data.threats_detected || 0,
  highSeverity: highSev,
  mediumSeverity: medSev,
  lowSeverity: lowSev,
  threatBreakdown: data.threat_summary || {},
});

      showNotification(`Analysis complete — ${data.threats_detected || 0} threats found`);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
      showNotification('Failed to connect to backend. Is Flask running?', 'error');
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  const generateRealisticMix = async () => {
    try {
      const response = await axios.post(`${API_BASE}/generate-realistic-mix`, { 
        count: 100,
        threat_percentage: 15
      });
      
      showNotification(
        `Generated ${response.data.normal_logs} normal logs + ${response.data.threat_scenarios} threat scenarios`,
        'success'
      );
      
      await fetchAlerts();
    } catch (error) {
      showNotification('Failed to generate realistic mix', 'error');
    }
  };

  const simulateAttack = async (threatType) => {
    setDropdownOpen(false);
    try {
      const response = await axios.post(`${API_BASE}/simulate-attack`, {
        threat_type: threatType,
      });
      const label = formatThreatType(threatType);
      showNotification(`Simulated ${label} — ${response.data.logs_generated} logs generated`);
      await fetchAlerts();
    } catch (error) {
      showNotification(`Failed to simulate ${threatType}`, 'error');
    }
  };

  const clearLogs = async () => {
    try {
      await axios.delete(`${API_BASE}/logs`);
      setAlerts([]);
      setStats({ totalLogs: 0, totalThreats: 0, highSeverity: 0, threatBreakdown: {} });
      setExpandedRow(null);
      showNotification('All logs cleared');
    } catch (error) {
      showNotification('Failed to clear logs', 'error');
    }
  };

  const toggleRow = (index) => {
    setExpandedRow(expandedRow === index ? null : index);
  };

  // NEW: Impact Analysis Modal Functions
  const openImpactAnalysis = (alert) => {
    setSelectedAlert(alert);
    setShowImpactModal(true);
  };

  const closeImpactModal = () => {
    setShowImpactModal(false);
    setSelectedAlert(null);
  };

  useEffect(() => {
    const handleClick = (e) => {
      if (dropdownOpen && !e.target.closest('.relative')) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, [dropdownOpen]);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <StatusNotification notification={notification} onClose={() => setNotification(null)} />

      <header className="bg-slate-900/80 border-b border-slate-800 backdrop-blur-xl sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-cyan-500/20 rounded-xl flex items-center justify-center border border-cyan-500/30">
                <span className="text-xl">🛡️</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                  Threat Detection Dashboard
                </h1>
                <p className="text-slate-500 text-sm">
                  Real-time cybersecurity monitoring
                  {lastRefresh && (
                    <span className="ml-2 text-slate-600">• Last refresh: {lastRefresh}</span>
                  )}
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                onClick={generateRealisticMix}
                className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-all duration-200 hover:shadow-lg"
              >
                <span>🎲</span>
                <span>Generate Realistic Mix</span>
              </button>

              <AttackDropdown
                isOpen={dropdownOpen}
                onToggle={() => setDropdownOpen(!dropdownOpen)}
                onSelect={simulateAttack}
                isLoading={loading}
              />

              <button
                onClick={clearLogs}
                className="flex items-center gap-2 px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white font-semibold rounded-lg transition-all duration-200 border border-slate-700 hover:border-slate-600"
              >
                <span>🗑️</span>
                <span>Clear Logs</span>
              </button>

              <button
                onClick={fetchAlerts}
                disabled={loading}
                className="flex items-center gap-2 px-5 py-2.5 bg-cyan-600 hover:bg-cyan-700 disabled:bg-cyan-800 disabled:opacity-50 text-white font-semibold rounded-lg transition-all duration-200 shadow-lg shadow-cyan-900/30 hover:shadow-cyan-900/50"
              >
                <span className={loading ? 'animate-spin' : ''}>🔄</span>
                <span>Refresh Alerts</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard icon="📊" label="Total Logs" value={stats.totalLogs} colorClass="text-cyan-400" />
          <StatsCard icon="🚨" label="Threats Detected" value={stats.totalThreats} colorClass={stats.totalThreats > 0 ? 'text-red-400' : 'text-emerald-400'} />
          <StatsCard icon="🔴" label="High Severity" value={stats.highSeverity} colorClass={stats.highSeverity > 0 ? 'text-red-400' : 'text-slate-400'} />
          <StatsCard icon="🟡" label="Medium Severity" value={stats.mediumSeverity} colorClass={stats.mediumSeverity > 0 ? 'text-amber-400' : 'text-slate-400'} />
<StatsCard icon="🟢" label="Low Severity" value={stats.lowSeverity} colorClass={stats.lowSeverity > 0 ? 'text-emerald-400' : 'text-slate-400'} /><StatsCard icon="📈" label="Threat Types" value={Object.keys(stats.threatBreakdown).length} colorClass="text-purple-400" />
        </div>

        {Object.keys(stats.threatBreakdown).length > 0 && (
          <div className="flex flex-wrap gap-2 animate-fade-in">
            {Object.entries(stats.threatBreakdown).map(([type, count]) => (
              <span key={type} className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium border ${getThreatBadgeColor(type)}`}>
                {THREAT_TYPES.find(t => t.value === type)?.icon || '⚠️'}
                {formatThreatType(type)}: {count}
              </span>
            ))}
          </div>
        )}

        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden shadow-xl shadow-black/20">
          <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-bold text-white">Detected Threats</h2>
              {alerts.length > 0 && (
                <span className="bg-red-500/20 text-red-400 px-2.5 py-0.5 rounded-full text-xs font-bold border border-red-500/30">
                  {alerts.length}
                </span>
              )}
            </div>
            {alerts.length > 0 && (
              <p className="text-sm text-slate-500">Click any row to expand details</p>
            )}
          </div>

          {loading ? (
            <LoadingSpinner />
          ) : alerts.length === 0 ? (
            <EmptyState />
          ) : (
            <AlertsTable 
              alerts={alerts} 
              expandedRow={expandedRow} 
              onToggleRow={toggleRow}
              onOpenImpact={openImpactAnalysis}  // PASS THE NEW PROP
            />
          )}
        </div>
      </main>

      <footer className="border-t border-slate-800 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className="text-slate-600 text-sm">
            🛡️ Threat Detection Dashboard • Rule-Based Anomaly Detection
          </p>
          <p className="text-slate-700 text-sm">
            Connected to <code className="text-slate-500">{API_BASE}</code>
          </p>
        </div>
      </footer>

      {/* IMPACT ANALYSIS MODAL (NEW) */}
      {showImpactModal && selectedAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
          <div className="bg-slate-900 rounded-2xl border border-slate-700 shadow-2xl shadow-black/50 
                         w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
            
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm 
                                font-bold border ${impactLevelColors[selectedAlert.impact?.impact_level || 'medium']}`}>
                  {formatThreatType(selectedAlert.threat_type)}
                </span>
                <span className="text-2xl font-bold text-white">
                  Impact Analysis
                </span>
                <span className={`inline-flex px-2.5 py-1 rounded-md text-sm font-bold border 
                                ${impactLevelColors[selectedAlert.impact?.impact_level || 'medium']}`}>
                  Score: {selectedAlert.anomaly_score?.toFixed(2)}
                </span>
              </div>
              
              <button
                onClick={closeImpactModal}
                className="w-10 h-10 rounded-lg bg-slate-800 hover:bg-slate-700 flex items-center justify-center 
                         text-slate-400 hover:text-white transition-colors duration-200"
              >
                ✕
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto px-6 py-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left Column: Attack Timeline */}
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <span className="w-2 h-2 bg-cyan-400 rounded-full"></span>
                    Attack Timeline
                  </h3>
                  <div className="bg-slate-800/30 rounded-lg p-4 border border-slate-700/50">
                    <AttackTimeline timeline={selectedAlert.attack_timeline} />
                  </div>
                </div>

                {/* Right Column: Impact Summary */}
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <span className="w-2 h-2 bg-purple-400 rounded-full"></span>
                    Impact Summary
                  </h3>
                  <div className="bg-slate-800/30 rounded-lg p-4 border border-slate-700/50">
                    <ImpactSummary impact={selectedAlert.impact} />
                  </div>
                </div>
              </div>

              {/* Alert Details Footer */}
              <div className="mt-6 pt-6 border-t border-slate-800">
                <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-3">
                  Alert Details
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-slate-500">User</p>
                    <p className="text-white font-medium">{selectedAlert.log?.user || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-slate-500">Action</p>
                    <p className="text-white font-medium">{selectedAlert.log?.action || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-slate-500">IP Address</p>
                    <p className="text-white font-medium">{selectedAlert.log?.ip || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-slate-500">Timestamp</p>
                    <p className="text-white font-medium">{selectedAlert.log?.timestamp || 'N/A'}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
