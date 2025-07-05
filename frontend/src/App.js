import React, { useState, useEffect } from 'react';
import './App.css';

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
  const [dashboardStats, setDashboardStats] = useState({});

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
    notes: ''
  });

  // Operational Log form state
  const [logForm, setLogForm] = useState({
    action: '',
    details: '',
    priority: 'normale',
    event_id: ''
  });

  // Filter states
  const [logFilters, setLogFilters] = useState({
    priority: '',
    startDate: '',
    endDate: '',
    operator: ''
  });

  // Check authentication on mount
  useEffect(() => {
    if (token) {
      checkAuth();
    }
  }, [token]);

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
      const [statsRes, eventsRes, logsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/dashboard/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_BASE_URL}/api/events`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch(`${API_BASE_URL}/api/logs`, {
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
          notes: ''
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
            
            <button
              onClick={() => setCurrentView('events')}
              className={`py-4 px-2 border-b-2 font-medium text-sm ${
                currentView === 'events' 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Eventi di Emergenza
            </button>
            
            {canAccess(['admin', 'coordinator', 'operator']) && (
              <button
                onClick={() => setCurrentView('create-event')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  currentView === 'create-event' 
                    ? 'border-blue-500 text-blue-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Nuovo Evento
              </button>
            )}
            
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
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
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
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Create Event View */}
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
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Inventario Magazzino</h3>
            </div>
            <div className="px-6 py-4">
              <p className="text-gray-500">Modulo inventario in fase di sviluppo...</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;