import React, { useState, useEffect } from 'react';
import './App.css';
import InventoryManagement from './components/InventoryManagement';
import UserManagement from './components/UserManagement';
import EmergencyEventsMap from './components/EmergencyEventsMap';

// Icons as simple SVG components
const AlertIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
  </svg>
);

const MapIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
  </svg>
);

const InventoryIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
  </svg>
);

const LogIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

const UserIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
  </svg>
);

const LoginIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
  </svg>
);

const PlusIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
  </svg>
);

const ReportIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

const DownloadIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

const PrintIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
  </svg>
);

const EditIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
  </svg>
);

const DeleteIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
);

const WarningIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
  </svg>
);

const AdminIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const ChevronDownIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
  </svg>
);

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [currentView, setCurrentView] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // States for different modules
  const [events, setEvents] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [logs, setLogs] = useState([]);
  const [resources, setResources] = useState([]);
  const [users, setUsers] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({});
  const [inventoryAlerts, setInventoryAlerts] = useState({});
  const [permissions, setPermissions] = useState({});
  const [editingEvent, setEditingEvent] = useState(null);
  const [showEventsMenu, setShowEventsMenu] = useState(false);
  const [showPermissionsModal, setShowPermissionsModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState('');
  const [rolePermissions, setRolePermissions] = useState([]);
  const [allPermissions, setAllPermissions] = useState([]);
  const [currentPermissions, setCurrentPermissions] = useState({});
  const [roles, setRoles] = useState({});

  // Login form state
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });

  // Event form state
  const [eventForm, setEventForm] = useState({
    title: '',
    description: '',
    event_type: 'incendio',
    severity: 'media',
    latitude: '',
    longitude: '',
    address: '',
    resources_needed: [],
    notes: '',
    status: 'aperto'
  });

  // Operational Log form state
  const [logForm, setLogForm] = useState({
    action: '',
    details: '',
    priority: 'normale',
    event_id: ''
  });

  // Inventory form state
  const [inventoryForm, setInventoryForm] = useState({
    name: '',
    category: '',
    quantity: 0,
    unit: 'pz',
    location: '',
    min_quantity: 0,
    max_quantity: '',
    expiry_date: '',
    supplier: '',
    cost_per_unit: '',
    notes: ''
  });

  // User management form state
  const [userForm, setUserForm] = useState({
    username: '',
    email: '',
    password: '',
    role: 'viewer',
    full_name: '',
    active: true
  });

  // Filter states
  const [logFilters, setLogFilters] = useState({
    priority: '',
    startDate: '',
    endDate: '',
    operator: ''
  });

  const [inventoryFilters, setInventoryFilters] = useState({
    category: '',
    location: '',
    low_stock: false,
    expiring_soon: false
  });

  // Report states
  const [reportTemplates, setReportTemplates] = useState({});
  const [reportForm, setReportForm] = useState({
    report_type: 'events',
    format: 'pdf',
    start_date: '',
    end_date: '',
    event_type: '',
    severity: '',
    priority: '',
    operator: '',
    status: ''
  });
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  // Check authentication on mount
  useEffect(() => {
    if (token) {
      checkAuth();
    }
  }, [token]);

  useEffect(() => {
    if (user?.role === 'admin') {
      loadPermissions();
    }
  }, [user]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showEventsMenu && !event.target.closest('.events-dropdown')) {
        setShowEventsMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showEventsMenu]);

  const checkAuth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        loadDashboardData();
      } else {
        logout();
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      logout();
    }
  };

  const login = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm)
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setToken(data.access_token);
        localStorage.setItem('token', data.access_token);
        setUser(data.user);
        setSuccess('Login effettuato con successo!');
        loadDashboardData();
        if (data.user.role === 'admin') {
          loadPermissions();
        }
      } else {
        setError(data.detail || 'Errore durante il login');
      }
    } catch (error) {
      setError('Errore di connessione al server');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    setCurrentView('dashboard');
  };

  const loadDashboardData = async () => {
    if (!token) return;
    
    try {
      const [statsRes, eventsRes, logsRes, inventoryRes, alertsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/dashboard/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_BASE_URL}/api/events`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_BASE_URL}/api/logs`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_BASE_URL}/api/inventory`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_BASE_URL}/api/inventory/alerts`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      if (statsRes.ok) {
        const stats = await statsRes.json();
        setDashboardStats(stats);
      }
      
      if (eventsRes.ok) {
        const eventsData = await eventsRes.json();
        setEvents(eventsData);
      }

      if (logsRes.ok) {
        const logsData = await logsRes.json();
        setLogs(logsData);
      }

      if (inventoryRes.ok) {
        const inventoryData = await inventoryRes.json();
        setInventory(inventoryData);
      }

      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        setInventoryAlerts(alertsData);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const createEvent = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          title: eventForm.title,
          description: eventForm.description,
          event_type: eventForm.event_type,
          severity: eventForm.severity,
          latitude: eventForm.latitude ? parseFloat(eventForm.latitude) : null,
          longitude: eventForm.longitude ? parseFloat(eventForm.longitude) : null,
          address: eventForm.address || null,
          notes: eventForm.notes || null,
          resources_needed: eventForm.resources_needed || [],
          status: "aperto",
          created_by: user.username
        })
      });
      
      if (response.ok) {
        setSuccess('Evento creato con successo!');
        setEventForm({
          title: '',
          description: '',
          event_type: 'incendio',
          severity: 'media',
          latitude: '',
          longitude: '',
          address: '',
          resources_needed: [],
          notes: '',
          status: 'aperto'
        });
        loadDashboardData();
        setCurrentView('events');
      } else {
        const data = await response.json();
        // Handle different error response formats
        if (typeof data.detail === 'string') {
          setError(data.detail);
        } else if (Array.isArray(data.detail)) {
          const errorMessages = data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
          setError(`Errori di validazione: ${errorMessages}`);
        } else {
          setError('Errore durante la creazione dell\'evento');
        }
      }
    } catch (error) {
      setError('Errore di connessione al server');
    } finally {
      setLoading(false);
    }
  };

  const updateEvent = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/events/${editingEvent.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          title: eventForm.title,
          description: eventForm.description,
          event_type: eventForm.event_type,
          severity: eventForm.severity,
          latitude: eventForm.latitude ? parseFloat(eventForm.latitude) : null,
          longitude: eventForm.longitude ? parseFloat(eventForm.longitude) : null,
          address: eventForm.address || null,
          notes: eventForm.notes || null,
          resources_needed: eventForm.resources_needed || [],
          status: eventForm.status || "aperto"
        })
      });
      
      if (response.ok) {
        setSuccess('Evento aggiornato con successo!');
        setEditingEvent(null);
        setEventForm({
          title: '',
          description: '',
          event_type: 'incendio',
          severity: 'media',
          latitude: '',
          longitude: '',
          address: '',
          resources_needed: [],
          notes: '',
          status: 'aperto'
        });
        loadDashboardData();
        setCurrentView('events');
      } else {
        const data = await response.json();
        setError(data.detail || 'Errore durante l\'aggiornamento dell\'evento');
      }
    } catch (error) {
      setError('Errore di connessione al server');
    } finally {
      setLoading(false);
    }
  };

  const startEditingEvent = (event) => {
    setEditingEvent(event);
    setEventForm({
      title: event.title,
      description: event.description,
      event_type: event.event_type,
      severity: event.severity,
      latitude: event.latitude?.toString() || '',
      longitude: event.longitude?.toString() || '',
      address: event.address || '',
      resources_needed: event.resources_needed || [],
      notes: event.notes || '',
      status: event.status || 'aperto'
    });
    setCurrentView('edit-event');
  };

  const cancelEditingEvent = () => {
    setEditingEvent(null);
    setEventForm({
      title: '',
      description: '',
      event_type: 'incendio',
      severity: 'media',
      latitude: '',
      longitude: '',
      address: '',
      resources_needed: [],
      notes: '',
      status: 'aperto'
    });
    setCurrentView('events');
  };

  const loadPermissions = async () => {
    if (!token || user?.role !== 'admin') return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/permissions`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAllPermissions(data.all_permissions);
        setCurrentPermissions(data.current_permissions);
        setRoles(data.roles);
      }
    } catch (error) {
      console.error('Failed to load permissions:', error);
    }
  };

  const loadRolePermissions = async (role) => {
    if (!token || user?.role !== 'admin') return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/permissions/${role}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setRolePermissions(data.permissions || []);
      }
    } catch (error) {
      console.error('Failed to load role permissions:', error);
    }
  };

  const updateRolePermissions = async (role, permissions) => {
    if (!token || user?.role !== 'admin') return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/permissions/${role}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          permissions: permissions,
          description: `Permessi aggiornati per ${roles[role] || role}`
        })
      });
      
      if (response.ok) {
        setSuccess(`Permessi aggiornati per il ruolo ${roles[role] || role}`);
        loadPermissions(); // Reload permissions
      } else {
        const data = await response.json();
        setError(data.detail || 'Errore durante l\'aggiornamento dei permessi');
      }
    } catch (error) {
      setError('Errore di connessione al server');
    }
  };

  const createLog = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/logs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          action: logForm.action,
          details: logForm.details,
          priority: logForm.priority,
          event_id: logForm.event_id || null
        })
      });
      
      if (response.ok) {
        setSuccess('Log operativo creato con successo!');
        setLogForm({
          action: '',
          details: '',
          priority: 'normale',
          event_id: ''
        });
        loadDashboardData();
        setCurrentView('logs');
      } else {
        const data = await response.json();
        // Handle different error response formats
        if (typeof data.detail === 'string') {
          setError(data.detail);
        } else if (Array.isArray(data.detail)) {
          const errorMessages = data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
          setError(`Errori di validazione: ${errorMessages}`);
        } else {
          setError('Errore durante la creazione del log');
        }
      }
    } catch (error) {
      setError('Errore di connessione al server');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critica': return 'bg-red-100 text-red-800';
      case 'alta': return 'bg-orange-100 text-orange-800';
      case 'media': return 'bg-yellow-100 text-yellow-800';
      case 'bassa': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'alta': return 'bg-red-100 text-red-800';
      case 'normale': return 'bg-yellow-100 text-yellow-800';
      case 'bassa': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredLogs = logs.filter(log => {
    const matchesPriority = !logFilters.priority || log.priority === logFilters.priority;
    const matchesOperator = !logFilters.operator || log.operator.toLowerCase().includes(logFilters.operator.toLowerCase());
    const matchesDate = (!logFilters.startDate || new Date(log.timestamp) >= new Date(logFilters.startDate)) &&
                       (!logFilters.endDate || new Date(log.timestamp) <= new Date(logFilters.endDate));
    return matchesPriority && matchesOperator && matchesDate;
  });

  // Load report templates
  const loadReportTemplates = async () => {
    if (!token) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/reports/templates`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setReportTemplates(data);
      }
    } catch (error) {
      console.error('Failed to load report templates:', error);
    }
  };

  // Generate report
  const generateReport = async (e) => {
    e.preventDefault();
    setIsGeneratingReport(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/reports/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(reportForm)
      });
      
      if (response.ok) {
        // Get filename from response headers
        const contentDisposition = response.headers.get('content-disposition');
        const filename = contentDisposition 
          ? contentDisposition.split('filename=')[1].replace(/"/g, '')
          : `report_${reportForm.report_type}_${new Date().getTime()}.${reportForm.format === 'pdf' ? 'pdf' : 'xlsx'}`;
        
        // Download file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        setSuccess('Report generato e scaricato con successo!');
      } else {
        const data = await response.json();
        setError(data.detail || 'Errore durante la generazione del report');
      }
    } catch (error) {
      setError('Errore di connessione al server');
    } finally {
      setIsGeneratingReport(false);
    }
  };

  // Load report templates when accessing reports
  useEffect(() => {
    if (currentView === 'reports') {
      loadReportTemplates();
    }
  }, [currentView]);

  // Load users when accessing admin panel
  const loadUsers = async () => {
    if (!token || user.role !== 'admin') return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  };

  useEffect(() => {
    if (currentView === 'admin' && user && user.role === 'admin') {
      loadUsers();
    }
  }, [currentView, user]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'aperto': return 'bg-red-100 text-red-800';
      case 'in_corso': return 'bg-yellow-100 text-yellow-800';
      case 'risolto': return 'bg-blue-100 text-blue-800';
      case 'chiuso': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const canAccess = (requiredRoles) => {
    return user && requiredRoles.includes(user.role);
  };

  // Clear messages after 5 seconds
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError('');
        setSuccess('');
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="max-w-md w-full space-y-8 p-8">
          <div className="text-center">
            <AlertIcon className="mx-auto h-12 w-12 text-red-600" />
            <h2 className="mt-6 text-3xl font-bold text-gray-900">
              Sistema Gestione Emergenze
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Accedi al sistema per gestire le emergenze
            </p>
          </div>
          
          <form className="mt-8 space-y-6" onSubmit={login}>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  value={loginForm.username}
                  onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            </div>
            
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}
            
            {success && (
              <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                {success}
              </div>
            )}
            
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400"
            >
              {loading ? 'Accesso in corso...' : 'Accedi'}
            </button>
          </form>
          
          <div className="text-center text-sm text-gray-600">
            <p>Credenziali di prova:</p>
            <p><strong>Admin:</strong> admin / admin123</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <AlertIcon className="h-8 w-8 text-red-600" />
              <h1 className="text-2xl font-bold text-gray-900">
                Sistema Gestione Emergenze
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {user.full_name} ({user.role})
              </span>
              <button
                onClick={logout}
                className="flex items-center space-x-2 text-red-600 hover:text-red-700"
              >
                <LoginIcon className="h-5 w-5" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setCurrentView('dashboard')}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                currentView === 'dashboard' 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Dashboard
            </button>
            
            {/* Events Dropdown */}
            <div className="relative events-dropdown">
              <button
                onClick={() => setShowEventsMenu(!showEventsMenu)}
                className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center space-x-1 ${
                  ['events', 'create-event', 'edit-event', 'map', 'event-types'].includes(currentView) 
                    ? 'border-blue-500 text-blue-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <span>Eventi</span>
                <ChevronDownIcon />
              </button>
              
              {showEventsMenu && (
                <div className="absolute top-full left-0 mt-1 w-48 bg-white rounded-md shadow-lg border z-50">
                  <div className="py-1">
                    <button
                      onClick={() => {
                        setCurrentView('events');
                        setShowEventsMenu(false);
                      }}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Eventi di Emergenza
                    </button>
                    {canAccess(['admin', 'coordinator', 'operator']) && (
                      <button
                        onClick={() => {
                          setCurrentView('create-event');
                          setShowEventsMenu(false);
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Nuovo Evento
                      </button>
                    )}
                    <button
                      onClick={() => {
                        setCurrentView('map');
                        setShowEventsMenu(false);
                      }}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Mappa Eventi
                    </button>
                    {canAccess(['admin', 'coordinator']) && (
                      <button
                        onClick={() => {
                          setCurrentView('event-types');
                          setShowEventsMenu(false);
                        }}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Tipi di Evento
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
            
            {canAccess(['admin', 'coordinator', 'operator']) && (
              <button
                onClick={() => setCurrentView('logs')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  currentView === 'logs' 
                    ? 'border-blue-500 text-blue-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Diario Operativo
              </button>
            )}
            
            {canAccess(['admin', 'coordinator', 'operator']) && (
              <button
                onClick={() => setCurrentView('create-log')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  currentView === 'create-log' 
                    ? 'border-blue-500 text-blue-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Nuovo Log
              </button>
            )}
            
            <button
              onClick={() => setCurrentView('reports')}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                currentView === 'reports' 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Reportistica
            </button>
            
            {canAccess(['admin', 'coordinator', 'warehouse']) && (
              <button
                onClick={() => setCurrentView('inventory')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  currentView === 'inventory' 
                    ? 'border-blue-500 text-blue-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Inventario
              </button>
            )}
            
            {user && user.role === 'admin' && (
              <button
                onClick={() => setCurrentView('admin')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  currentView === 'admin' 
                    ? 'border-blue-500 text-blue-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Amministrazione
              </button>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}
        
        {success && (
          <div className="mb-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
            {success}
          </div>
        )}

        {/* Dashboard View */}
        {currentView === 'dashboard' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Eventi Totali</p>
                    <p className="text-2xl font-bold text-gray-900">{dashboardStats.total_events || 0}</p>
                  </div>
                  <AlertIcon className="h-8 w-8 text-blue-600" />
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Eventi Aperti</p>
                    <p className="text-2xl font-bold text-red-600">{dashboardStats.open_events || 0}</p>
                  </div>
                  <AlertIcon className="h-8 w-8 text-red-600" />
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Eventi Critici</p>
                    <p className="text-2xl font-bold text-red-800">{dashboardStats.critical_events || 0}</p>
                  </div>
                  <AlertIcon className="h-8 w-8 text-red-800" />
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Log Operativi</p>
                    <p className="text-2xl font-bold text-blue-600">{dashboardStats.total_logs || 0}</p>
                  </div>
                  <LogIcon className="h-8 w-8 text-blue-600" />
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Articoli Inventario</p>
                    <p className="text-2xl font-bold text-green-600">{dashboardStats.inventory_items || 0}</p>
                  </div>
                  <InventoryIcon className="h-8 w-8 text-green-600" />
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Risorse Formate</p>
                    <p className="text-2xl font-bold text-purple-600">{dashboardStats.trained_resources || 0}</p>
                  </div>
                  <UserIcon className="h-8 w-8 text-purple-600" />
                </div>
              </div>
            </div>
            
            {/* Recent Events */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Eventi Recenti</h3>
              </div>
              <div className="px-6 py-4">
                {events.length === 0 ? (
                  <p className="text-gray-500">Nessun evento presente</p>
                ) : (
                  <div className="space-y-4">
                    {events.slice(0, 5).map((event) => (
                      <div key={event.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <h4 className="font-medium text-gray-900">{event.title}</h4>
                            <span className={`px-2 py-1 text-xs rounded-full ${getSeverityColor(event.severity)}`}>
                              {event.severity}
                            </span>
                            <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(event.status)}`}>
                              {event.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600">{event.description}</p>
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            <span>Tipo: {event.event_type}</span>
                            {event.address && <span>Indirizzo: {event.address}</span>}
                            <span>Creato: {new Date(event.created_at).toLocaleString()}</span>
                          </div>
                        </div>
                        {(event.latitude && event.longitude) && (
                          <MapIcon className="h-5 w-5 text-blue-600" />
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Recent Operational Logs */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium text-gray-900">Log Operativi Recenti</h3>
                  <button
                    onClick={() => setCurrentView('logs')}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    Visualizza tutti
                  </button>
                </div>
              </div>
              <div className="px-6 py-4">
                {logs.length === 0 ? (
                  <p className="text-gray-500">Nessun log operativo presente</p>
                ) : (
                  <div className="space-y-3">
                    {logs.slice(0, 5).map((log) => (
                      <div key={log.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <LogIcon className="h-4 w-4 text-gray-400" />
                            <h4 className="font-medium text-gray-900">{log.action}</h4>
                            <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(log.priority)}`}>
                              {log.priority}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">{log.details}</p>
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                            <span>Operatore: {log.operator}</span>
                            <span>Data: {new Date(log.timestamp).toLocaleString()}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Events View */}
        {currentView === 'events' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Tutti gli Eventi di Emergenza</h3>
            </div>
            <div className="px-6 py-4">
              {events.length === 0 ? (
                <p className="text-gray-500">Nessun evento presente</p>
              ) : (
                <div className="space-y-4">
                  {events.map((event) => (
                    <div key={event.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <h4 className="font-medium text-gray-900">{event.title}</h4>
                          <span className={`px-2 py-1 text-xs rounded-full ${getSeverityColor(event.severity)}`}>
                            {event.severity}
                          </span>
                          <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(event.status)}`}>
                            {event.status}
                          </span>
                        </div>
                        {(event.latitude && event.longitude) && (
                          <div className="flex items-center space-x-1 text-blue-600">
                            <MapIcon className="h-4 w-4" />
                            <span className="text-sm">Geolocalizzato</span>
                          </div>
                        )}
                      </div>
                      
                      <p className="text-gray-600 mb-3">{event.description}</p>
                      
                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="font-medium">Tipo:</span> {event.event_type}
                        </div>
                        <div>
                          <span className="font-medium">Creato da:</span> {event.created_by}
                        </div>
                        <div>
                          <span className="font-medium">Data:</span> {new Date(event.created_at).toLocaleString()}
                        </div>
                        {event.address && (
                          <div>
                            <span className="font-medium">Indirizzo:</span> {event.address}
                          </div>
                        )}
                      </div>
                      
                      {(event.latitude && event.longitude) && (
                        <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                          <div className="flex items-center space-x-2">
                            <MapIcon className="h-4 w-4 text-blue-600" />
                            <span className="text-sm font-medium">Coordinate:</span>
                            <span className="text-sm">
                              {event.latitude.toFixed(6)}, {event.longitude.toFixed(6)}
                            </span>
                          </div>
                        </div>
                      )}
                      
                      {event.notes && (
                        <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm font-medium">Note:</span>
                          <p className="text-sm text-gray-600 mt-1">{event.notes}</p>
                        </div>
                      )}
                      
                      {/* Edit Button for authorized users */}
                      {canAccess(['admin', 'coordinator', 'operator']) && (
                        <div className="mt-4 flex justify-end">
                          <button
                            onClick={() => startEditingEvent(event)}
                            className="flex items-center space-x-2 px-4 py-2 bg-yellow-600 text-white rounded-md text-sm hover:bg-yellow-700"
                          >
                            <EditIcon />
                            <span>Modifica Evento</span>
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Map View */}
        {currentView === 'map' && (
          <EmergencyEventsMap
            token={token}
            setError={setError}
            setSuccess={setSuccess}
            API_BASE_URL={API_BASE_URL}
          />
        )}

        {/* Edit Event View */}
        {currentView === 'edit-event' && editingEvent && canAccess(['admin', 'coordinator', 'operator']) && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Modifica Evento di Emergenza</h3>
            </div>
            <div className="px-6 py-4">
              <form onSubmit={updateEvent} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Titolo Evento *
                    </label>
                    <input
                      type="text"
                      value={eventForm.title}
                      onChange={(e) => setEventForm({ ...eventForm, title: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tipo di Evento *
                    </label>
                    <select
                      value={eventForm.event_type}
                      onChange={(e) => setEventForm({ ...eventForm, event_type: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="incendio">Incendio</option>
                      <option value="terremoto">Terremoto</option>
                      <option value="alluvione">Alluvione</option>
                      <option value="valanga">Valanga</option>
                      <option value="frana">Frana</option>
                      <option value="incidente_stradale">Incidente Stradale</option>
                      <option value="emergenza_sanitaria">Emergenza Sanitaria</option>
                      <option value="emergenza_ambientale">Emergenza Ambientale</option>
                      <option value="altro">Altro</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Descrizione *
                  </label>
                  <textarea
                    value={eventForm.description}
                    onChange={(e) => setEventForm({ ...eventForm, description: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Gravità *
                    </label>
                    <select
                      value={eventForm.severity}
                      onChange={(e) => setEventForm({ ...eventForm, severity: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="bassa">Bassa</option>
                      <option value="media">Media</option>
                      <option value="alta">Alta</option>
                      <option value="critica">Critica</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Status *
                    </label>
                    <select
                      value={eventForm.status}
                      onChange={(e) => setEventForm({ ...eventForm, status: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="aperto">Aperto</option>
                      <option value="in_corso">In Corso</option>
                      <option value="risolto">Risolto</option>
                      <option value="chiuso">Chiuso</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Indirizzo
                  </label>
                  <input
                    type="text"
                    value={eventForm.address}
                    onChange={(e) => setEventForm({ ...eventForm, address: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Indirizzo o località dell'evento"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Coordinate GPS
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <input
                        type="number"
                        step="any"
                        value={eventForm.latitude}
                        onChange={(e) => setEventForm({ ...eventForm, latitude: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Latitudine (es: 45.4642)"
                      />
                    </div>
                    <div>
                      <input
                        type="number"
                        step="any"
                        value={eventForm.longitude}
                        onChange={(e) => setEventForm({ ...eventForm, longitude: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Longitudine (es: 9.1900)"
                      />
                    </div>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">
                    Inserisci le coordinate GPS per geolocalizzare l'evento. Puoi ottenerle da Google Maps o altri servizi di mappe.
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Note aggiuntive
                  </label>
                  <textarea
                    value={eventForm.notes}
                    onChange={(e) => setEventForm({ ...eventForm, notes: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Informazioni aggiuntive, risorse richieste, etc."
                  />
                </div>
                
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={cancelEditingEvent}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Annulla
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-400"
                  >
                    {loading ? 'Aggiornamento...' : 'Aggiorna Evento'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
        {currentView === 'create-event' && canAccess(['admin', 'coordinator', 'operator']) && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Crea Nuovo Evento di Emergenza</h3>
            </div>
            <div className="px-6 py-4">
              <form onSubmit={createEvent} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Titolo Evento *
                    </label>
                    <input
                      type="text"
                      value={eventForm.title}
                      onChange={(e) => setEventForm({ ...eventForm, title: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tipo di Evento *
                    </label>
                    <select
                      value={eventForm.event_type}
                      onChange={(e) => setEventForm({ ...eventForm, event_type: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="incendio">Incendio</option>
                      <option value="alluvione">Alluvione</option>
                      <option value="terremoto">Terremoto</option>
                      <option value="incidente_stradale">Incidente Stradale</option>
                      <option value="emergenza_medica">Emergenza Medica</option>
                      <option value="blackout">Blackout</option>
                      <option value="altro">Altro</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Descrizione *
                  </label>
                  <textarea
                    value={eventForm.description}
                    onChange={(e) => setEventForm({ ...eventForm, description: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Gravità
                    </label>
                    <select
                      value={eventForm.severity}
                      onChange={(e) => setEventForm({ ...eventForm, severity: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="bassa">Bassa</option>
                      <option value="media">Media</option>
                      <option value="alta">Alta</option>
                      <option value="critica">Critica</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Indirizzo
                    </label>
                    <input
                      type="text"
                      value={eventForm.address}
                      onChange={(e) => setEventForm({ ...eventForm, address: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Via, Città, Provincia"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Coordinate GPS (opzionale)
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <input
                        type="number"
                        step="any"
                        value={eventForm.latitude}
                        onChange={(e) => setEventForm({ ...eventForm, latitude: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Latitudine (es: 45.4642)"
                      />
                    </div>
                    <div>
                      <input
                        type="number"
                        step="any"
                        value={eventForm.longitude}
                        onChange={(e) => setEventForm({ ...eventForm, longitude: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Longitudine (es: 9.1900)"
                      />
                    </div>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">
                    Inserisci le coordinate GPS per geolocalizzare l'evento. Puoi ottenerle da Google Maps o altri servizi di mappe.
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Note aggiuntive
                  </label>
                  <textarea
                    value={eventForm.notes}
                    onChange={(e) => setEventForm({ ...eventForm, notes: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Informazioni aggiuntive, risorse richieste, etc."
                  />
                </div>
                
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setCurrentView('events')}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Annulla
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:bg-gray-400"
                  >
                    {loading ? 'Creazione...' : 'Crea Evento'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Inventory View */}
        {currentView === 'inventory' && canAccess(['admin', 'coordinator', 'warehouse']) && (
          <InventoryManagement
            token={token}
            inventory={inventory}
            setInventory={setInventory}
            inventoryFilters={inventoryFilters}
            setInventoryFilters={setInventoryFilters}
            inventoryForm={inventoryForm}
            setInventoryForm={setInventoryForm}
            user={user}
            setError={setError}
            setSuccess={setSuccess}
            loading={loading}
            setLoading={setLoading}
            API_BASE_URL={API_BASE_URL}
          />
        )}

        {/* User Management View (Admin Only) */}
        {currentView === 'admin' && (
          <div className="space-y-6">
            <UserManagement
              token={token}
              users={users}
              setUsers={setUsers}
              userForm={userForm}
              setUserForm={setUserForm}
              user={user}
              setError={setError}
              setSuccess={setSuccess}
              loading={loading}
              setLoading={setLoading}
              API_BASE_URL={API_BASE_URL}
            />
            
            {/* Permissions Management */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium text-gray-900">Gestione Permessi</h3>
                  <button
                    onClick={() => setShowPermissionsModal(true)}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
                  >
                    <AdminIcon className="h-4 w-4" />
                    <span>Modifica Permessi</span>
                  </button>
                </div>
              </div>
              <div className="px-6 py-4">
                {Object.keys(roles).length === 0 ? (
                  <p className="text-gray-500">Caricamento permessi...</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {Object.entries(roles).map(([roleKey, roleName]) => (
                      <div key={roleKey} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-medium text-gray-900">{roleName}</h4>
                          <button
                            onClick={() => {
                              setSelectedRole(roleKey);
                              loadRolePermissions(roleKey);
                              setShowPermissionsModal(true);
                            }}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            <EditIcon className="h-4 w-4" />
                          </button>
                        </div>
                        <div className="space-y-1">
                          {(currentPermissions[roleKey] || []).map((permission) => (
                            <span key={permission} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-1 mb-1">
                              {permission}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Permissions Modal */}
        {showPermissionsModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium text-gray-900">
                    Modifica Permessi - {selectedRole ? roles[selectedRole] : 'Seleziona Ruolo'}
                  </h3>
                  <button
                    onClick={() => {
                      setShowPermissionsModal(false);
                      setSelectedRole('');
                      setRolePermissions([]);
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              
              <div className="px-6 py-4">
                {!selectedRole ? (
                  <div className="space-y-4">
                    <p className="text-gray-600">Seleziona un ruolo per modificare i permessi:</p>
                    <div className="grid grid-cols-1 gap-3">
                      {Object.entries(roles).map(([roleKey, roleName]) => (
                        <button
                          key={roleKey}
                          onClick={() => {
                            setSelectedRole(roleKey);
                            loadRolePermissions(roleKey);
                          }}
                          className="p-3 text-left border border-gray-300 rounded-md hover:bg-gray-50"
                        >
                          <div className="font-medium">{roleName}</div>
                          <div className="text-sm text-gray-500">
                            {(currentPermissions[roleKey] || []).length} permessi attivi
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <p className="text-gray-600">
                      Seleziona i permessi per il ruolo <strong>{roles[selectedRole]}</strong>:
                    </p>
                    <div className="grid grid-cols-1 gap-3 max-h-96 overflow-y-auto">
                      {allPermissions.map((permission) => (
                        <label key={permission} className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            checked={rolePermissions.includes(permission)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setRolePermissions([...rolePermissions, permission]);
                              } else {
                                setRolePermissions(rolePermissions.filter(p => p !== permission));
                              }
                            }}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="text-sm text-gray-700">{permission}</span>
                        </label>
                      ))}
                    </div>
                    <div className="flex justify-end space-x-3 pt-4 border-t">
                      <button
                        onClick={() => {
                          setSelectedRole('');
                          setRolePermissions([]);
                        }}
                        className="px-4 py-2 text-gray-600 hover:text-gray-800"
                      >
                        Indietro
                      </button>
                      <button
                        onClick={() => {
                          updateRolePermissions(selectedRole, rolePermissions);
                          setShowPermissionsModal(false);
                          setSelectedRole('');
                          setRolePermissions([]);
                        }}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                      >
                        Salva Permessi
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Operational Logs View */}
        {currentView === 'logs' && canAccess(['admin', 'coordinator', 'operator']) && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900">Diario Operativo</h3>
                <div className="flex items-center space-x-4">
                  <select
                    value={logFilters.priority}
                    onChange={(e) => setLogFilters({ ...logFilters, priority: e.target.value })}
                    className="px-3 py-1 border border-gray-300 rounded-md text-sm"
                  >
                    <option value="">Tutte le priorità</option>
                    <option value="alta">Alta</option>
                    <option value="normale">Normale</option>
                    <option value="bassa">Bassa</option>
                  </select>
                  <input
                    type="text"
                    placeholder="Filtra per operatore"
                    value={logFilters.operator}
                    onChange={(e) => setLogFilters({ ...logFilters, operator: e.target.value })}
                    className="px-3 py-1 border border-gray-300 rounded-md text-sm"
                  />
                  <button
                    onClick={() => setCurrentView('create-log')}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
                  >
                    <PlusIcon />
                    <span>Nuovo Log</span>
                  </button>
                </div>
              </div>
            </div>
            <div className="px-6 py-4">
              {filteredLogs.length === 0 ? (
                <p className="text-gray-500">
                  {logs.length === 0 ? 'Nessun log operativo presente' : 'Nessun log corrispondente ai filtri'}
                </p>
              ) : (
                <div className="space-y-4">
                  {filteredLogs.map((log) => (
                    <div key={log.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <LogIcon className="h-5 w-5 text-gray-400" />
                          <h4 className="font-medium text-gray-900">{log.action}</h4>
                          <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(log.priority)}`}>
                            {log.priority}
                          </span>
                        </div>
                        <div className="text-sm text-gray-500">
                          {new Date(log.timestamp).toLocaleString()}
                        </div>
                      </div>
                      
                      <p className="text-gray-600 mb-3">{log.details}</p>
                      
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-4">
                          <span className="text-gray-500">
                            <strong>Operatore:</strong> {log.operator}
                          </span>
                          {log.event_id && (
                            <span className="text-blue-600">
                              <strong>Evento collegato:</strong> {log.event_id}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Create Log View */}
        {currentView === 'create-log' && canAccess(['admin', 'coordinator', 'operator']) && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Nuovo Log Operativo</h3>
            </div>
            <div className="px-6 py-4">
              <form onSubmit={createLog} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Azione/Attività *
                  </label>
                  <input
                    type="text"
                    value={logForm.action}
                    onChange={(e) => setLogForm({ ...logForm, action: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="es. Controllo magazzino, Riunione coordinamento, Aggiornamento status..."
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Dettagli *
                  </label>
                  <textarea
                    value={logForm.details}
                    onChange={(e) => setLogForm({ ...logForm, details: e.target.value })}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Descrizione dettagliata dell'attività svolta, risultati, note operative..."
                    required
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Priorità
                    </label>
                    <select
                      value={logForm.priority}
                      onChange={(e) => setLogForm({ ...logForm, priority: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="bassa">Bassa</option>
                      <option value="normale">Normale</option>
                      <option value="alta">Alta</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Evento Collegato (opzionale)
                    </label>
                    <select
                      value={logForm.event_id}
                      onChange={(e) => setLogForm({ ...logForm, event_id: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Nessun evento</option>
                      {events.filter(event => event.status === 'aperto' || event.status === 'in_corso').map((event) => (
                        <option key={event.id} value={event.id}>
                          {event.title} ({event.event_type})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-2">Informazioni Automatiche</h4>
                  <div className="text-sm text-gray-600 space-y-1">
                    <p><strong>Operatore:</strong> {user.full_name} ({user.username})</p>
                    <p><strong>Timestamp:</strong> {new Date().toLocaleString()}</p>
                  </div>
                </div>
                
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setCurrentView('logs')}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Annulla
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    {loading ? 'Creazione...' : 'Crea Log'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Reports View */}
        {currentView === 'reports' && (
          <div className="space-y-6">
            {/* Report Generation Card */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                  <ReportIcon className="h-6 w-6 text-blue-600" />
                  <h3 className="text-lg font-medium text-gray-900">Generazione Report</h3>
                </div>
              </div>
              <div className="px-6 py-4">
                <form onSubmit={generateReport} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Tipo di Report *
                      </label>
                      <select
                        value={reportForm.report_type}
                        onChange={(e) => setReportForm({ ...reportForm, report_type: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      >
                        <option value="events">Report Eventi di Emergenza</option>
                        <option value="logs">Report Log Operativi</option>
                        <option value="statistics">Report Statistiche Generali</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Formato *
                      </label>
                      <select
                        value={reportForm.format}
                        onChange={(e) => setReportForm({ ...reportForm, format: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      >
                        <option value="pdf">PDF (Stampa)</option>
                        <option value="excel">Excel (Analisi)</option>
                      </select>
                    </div>
                  </div>
                  
                  {reportForm.report_type !== 'statistics' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Data Inizio
                        </label>
                        <input
                          type="date"
                          value={reportForm.start_date}
                          onChange={(e) => setReportForm({ ...reportForm, start_date: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Data Fine
                        </label>
                        <input
                          type="date"
                          value={reportForm.end_date}
                          onChange={(e) => setReportForm({ ...reportForm, end_date: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                  )}
                  
                  {/* Filtri specifici per tipo di report */}
                  {reportForm.report_type === 'events' && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Tipo Evento
                        </label>
                        <select
                          value={reportForm.event_type}
                          onChange={(e) => setReportForm({ ...reportForm, event_type: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Tutti i tipi</option>
                          <option value="incendio">Incendio</option>
                          <option value="alluvione">Alluvione</option>
                          <option value="terremoto">Terremoto</option>
                          <option value="incidente_stradale">Incidente Stradale</option>
                          <option value="emergenza_medica">Emergenza Medica</option>
                          <option value="blackout">Blackout</option>
                          <option value="altro">Altro</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Gravità
                        </label>
                        <select
                          value={reportForm.severity}
                          onChange={(e) => setReportForm({ ...reportForm, severity: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Tutte le gravità</option>
                          <option value="bassa">Bassa</option>
                          <option value="media">Media</option>
                          <option value="alta">Alta</option>
                          <option value="critica">Critica</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Status
                        </label>
                        <select
                          value={reportForm.status}
                          onChange={(e) => setReportForm({ ...reportForm, status: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Tutti gli status</option>
                          <option value="aperto">Aperto</option>
                          <option value="in_corso">In Corso</option>
                          <option value="risolto">Risolto</option>
                          <option value="chiuso">Chiuso</option>
                        </select>
                      </div>
                    </div>
                  )}
                  
                  {reportForm.report_type === 'logs' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Priorità
                        </label>
                        <select
                          value={reportForm.priority}
                          onChange={(e) => setReportForm({ ...reportForm, priority: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Tutte le priorità</option>
                          <option value="bassa">Bassa</option>
                          <option value="normale">Normale</option>
                          <option value="alta">Alta</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Operatore
                        </label>
                        <input
                          type="text"
                          value={reportForm.operator}
                          onChange={(e) => setReportForm({ ...reportForm, operator: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="Nome operatore (opzionale)"
                        />
                      </div>
                    </div>
                  )}
                  
                  <div className="flex justify-end space-x-3">
                    <button
                      type="submit"
                      disabled={isGeneratingReport}
                      className="flex items-center space-x-2 px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400"
                    >
                      {isGeneratingReport ? (
                        <>
                          <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                          <span>Generazione...</span>
                        </>
                      ) : (
                        <>
                          <DownloadIcon />
                          <span>Genera e Scarica Report</span>
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </div>
            
            {/* Report Templates Info */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Tipi di Report Disponibili</h3>
              </div>
              <div className="px-6 py-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3 mb-3">
                      <AlertIcon className="h-6 w-6 text-red-600" />
                      <h4 className="font-medium text-gray-900">Eventi di Emergenza</h4>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                      Report dettagliato di tutti gli eventi di emergenza con filtri per tipo, gravità e periodo.
                    </p>
                    <div className="text-xs text-gray-500">
                      <p><strong>Formati:</strong> PDF, Excel</p>
                      <p><strong>Filtri:</strong> Data, Tipo, Gravità, Status</p>
                    </div>
                  </div>
                  
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3 mb-3">
                      <LogIcon className="h-6 w-6 text-blue-600" />
                      <h4 className="font-medium text-gray-900">Log Operativi</h4>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                      Report delle attività operative registrate nel sistema con dettagli per operatore e priorità.
                    </p>
                    <div className="text-xs text-gray-500">
                      <p><strong>Formati:</strong> PDF, Excel</p>
                      <p><strong>Filtri:</strong> Data, Priorità, Operatore</p>
                    </div>
                  </div>
                  
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3 mb-3">
                      <ReportIcon className="h-6 w-6 text-green-600" />
                      <h4 className="font-medium text-gray-900">Statistiche Generali</h4>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                      Riepilogo statistico completo del sistema con tutti i contatori e metriche principali.
                    </p>
                    <div className="text-xs text-gray-500">
                      <p><strong>Formati:</strong> PDF, Excel</p>
                      <p><strong>Contenuto:</strong> Dashboard statistiche</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;