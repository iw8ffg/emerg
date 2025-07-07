import React, { useState, useEffect } from 'react';

const UserManagement = ({ 
  token, 
  users, 
  setUsers, 
  userForm,
  setUserForm,
  user,
  setError,
  setSuccess,
  loading,
  setLoading,
  API_BASE_URL 
}) => {
  const [editingUser, setEditingUser] = useState(null);
  const [currentView, setCurrentView] = useState('list'); // list, create, edit
  const [adminStats, setAdminStats] = useState({});

  // Icons
  const PlusIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
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

  const UserIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  );

  const AdminIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  );

  // User roles with descriptions
  const USER_ROLES = {
    'admin': 'Amministratore',
    'coordinator': 'Coordinatore Emergenze',
    'operator': 'Operatore Sala Operativa',
    'warehouse': 'Addetto Magazzino',
    'viewer': 'Visualizzatore'
  };

  // Load users
  const loadUsers = async () => {
    if (!token) return;
    
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

  // Load admin statistics
  const loadAdminStats = async () => {
    if (!token) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAdminStats(data);
      }
    } catch (error) {
      console.error('Failed to load admin stats:', error);
    }
  };

  // Create or update user
  const saveUser = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const url = editingUser 
        ? `${API_BASE_URL}/api/admin/users/${editingUser.username}`
        : `${API_BASE_URL}/api/admin/users`;
      
      const method = editingUser ? 'PUT' : 'POST';
      
      let userData;
      if (editingUser) {
        userData = {
          email: userForm.email,
          role: userForm.role,
          full_name: userForm.full_name,
          active: userForm.active
        };
        if (userForm.password) {
          userData.new_password = userForm.password;
        }
      } else {
        userData = userForm;
      }
      
      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(userData)
      });
      
      if (response.ok) {
        setSuccess(editingUser ? 'Utente aggiornato con successo!' : 'Utente creato con successo!');
        setUserForm({
          username: '',
          email: '',
          password: '',
          role: 'viewer',
          full_name: '',
          active: true
        });
        setEditingUser(null);
        setCurrentView('list');
        loadUsers();
        loadAdminStats();
      } else {
        const data = await response.json();
        setError(data.detail || 'Errore durante il salvataggio');
      }
    } catch (error) {
      setError('Errore di connessione al server');
    } finally {
      setLoading(false);
    }
  };

  // Delete user
  const deleteUser = async (username, fullName) => {
    if (!window.confirm(`Sei sicuro di voler eliminare l'utente "${fullName}" (${username})?`)) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/users/${username}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        setSuccess('Utente eliminato con successo!');
        loadUsers();
        loadAdminStats();
      } else {
        const data = await response.json();
        setError(data.detail || 'Errore durante l\'eliminazione');
      }
    } catch (error) {
      setError('Errore di connessione al server');
    }
  };

  // Reset user password
  const resetPassword = async (username, fullName) => {
    if (!window.confirm(`Sei sicuro di voler resettare la password di "${fullName}"?`)) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/users/${username}/reset-password`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSuccess(data.message);
      } else {
        const data = await response.json();
        setError(data.detail || 'Errore durante il reset password');
      }
    } catch (error) {
      setError('Errore di connessione al server');
    }
  };

  // Start editing user
  const startEditing = (userData) => {
    setUserForm({
      username: userData.username,
      email: userData.email || '',
      password: '', // Don't populate password for editing
      role: userData.role || 'viewer',
      full_name: userData.full_name || '',
      active: userData.active !== false
    });
    setEditingUser(userData);
    setCurrentView('edit');
  };

  // Get role color
  const getRoleColor = (role) => {
    const colors = {
      'admin': 'bg-red-100 text-red-800',
      'coordinator': 'bg-purple-100 text-purple-800',
      'operator': 'bg-blue-100 text-blue-800',
      'warehouse': 'bg-green-100 text-green-800',
      'viewer': 'bg-gray-100 text-gray-800'
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  useEffect(() => {
    loadUsers();
    loadAdminStats();
  }, [token]);

  // Only admin can access user management
  if (user.role !== 'admin') {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center">
          <AdminIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Accesso negato</h3>
          <p className="mt-1 text-sm text-gray-500">
            Solo gli amministratori possono accedere alla gestione utenti.
          </p>
        </div>
      </div>
    );
  }

  if (currentView === 'create' || currentView === 'edit') {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            {currentView === 'create' ? 'Nuovo Utente' : 'Modifica Utente'}
          </h3>
        </div>
        <div className="px-6 py-4">
          <form onSubmit={saveUser} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Username *
                </label>
                <input
                  type="text"
                  value={userForm.username}
                  onChange={(e) => setUserForm({ ...userForm, username: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={currentView === 'edit'}
                  required
                />
                {currentView === 'edit' && (
                  <p className="text-xs text-gray-500 mt-1">Username non può essere modificato</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nome Completo *
                </label>
                <input
                  type="text"
                  value={userForm.full_name}
                  onChange={(e) => setUserForm({ ...userForm, full_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email *
                </label>
                <input
                  type="email"
                  value={userForm.email}
                  onChange={(e) => setUserForm({ ...userForm, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ruolo *
                </label>
                <select
                  value={userForm.role}
                  onChange={(e) => setUserForm({ ...userForm, role: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  {Object.entries(USER_ROLES).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {currentView === 'create' ? 'Password *' : 'Nuova Password (lascia vuoto per non cambiare)'}
              </label>
              <input
                type="password"
                value={userForm.password}
                onChange={(e) => setUserForm({ ...userForm, password: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required={currentView === 'create'}
                minLength="6"
              />
              {currentView === 'create' && (
                <p className="text-xs text-gray-500 mt-1">Minimo 6 caratteri</p>
              )}
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="active"
                checked={userForm.active}
                onChange={(e) => setUserForm({ ...userForm, active: e.target.checked })}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="active" className="ml-2 text-sm text-gray-700">
                Utente attivo
              </label>
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  setCurrentView('list');
                  setEditingUser(null);
                  setUserForm({
                    username: '',
                    email: '',
                    password: '',
                    role: 'viewer',
                    full_name: '',
                    active: true
                  });
                }}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Annulla
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400"
              >
                {loading ? 'Salvataggio...' : (currentView === 'create' ? 'Crea Utente' : 'Aggiorna Utente')}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  // Main user management view
  return (
    <div className="space-y-6">
      {/* Admin Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Utenti Totali</p>
              <p className="text-2xl font-bold text-gray-900">{adminStats?.users?.total || 0}</p>
            </div>
            <UserIcon className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Utenti Attivi</p>
              <p className="text-2xl font-bold text-green-600">{adminStats?.users?.active || 0}</p>
            </div>
            <UserIcon className="h-8 w-8 text-green-600" />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Eventi (7gg)</p>
              <p className="text-2xl font-bold text-purple-600">{adminStats?.recent_activity?.events_last_7_days || 0}</p>
            </div>
            <AdminIcon className="h-8 w-8 text-purple-600" />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Log (7gg)</p>
              <p className="text-2xl font-bold text-orange-600">{adminStats?.recent_activity?.logs_last_7_days || 0}</p>
            </div>
            <AdminIcon className="h-8 w-8 text-orange-600" />
          </div>
        </div>
      </div>

      {/* User Management */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">Gestione Utenti</h3>
            <button
              onClick={() => setCurrentView('create')}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
            >
              <PlusIcon />
              <span>Nuovo Utente</span>
            </button>
          </div>
        </div>
        
        <div className="px-6 py-4">
          {users.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              Nessun utente trovato
            </p>
          ) : (
            <div className="space-y-4">
              {users.map((userData) => (
                <div key={userData.username} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="font-medium text-gray-900">{userData.full_name}</h4>
                        <span className="text-sm text-gray-500">@{userData.username}</span>
                        <span className={`px-2 py-1 text-xs rounded-full ${getRoleColor(userData.role)}`}>
                          {USER_ROLES[userData.role]}
                        </span>
                        {!userData.active && (
                          <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">
                            Inattivo
                          </span>
                        )}
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div><strong>Email:</strong> {userData.email}</div>
                        <div><strong>Creato:</strong> {new Date(userData.created_at).toLocaleDateString()}</div>
                        {userData.created_by && <div><strong>Creato da:</strong> {userData.created_by}</div>}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => resetPassword(userData.username, userData.full_name)}
                        className="px-3 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-md hover:bg-yellow-200"
                        disabled={userData.username === user.username}
                      >
                        Reset Password
                      </button>
                      
                      <button
                        onClick={() => startEditing(userData)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-md"
                        disabled={userData.username === user.username}
                      >
                        <EditIcon />
                      </button>
                      
                      <button
                        onClick={() => deleteUser(userData.username, userData.full_name)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-md"
                        disabled={userData.username === user.username || userData.role === 'admin'}
                      >
                        <DeleteIcon />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Role Distribution */}
      {adminStats?.users?.by_role && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Distribuzione Ruoli</h3>
          </div>
          <div className="px-6 py-4">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(adminStats.users.by_role).map(([role, count]) => (
                <div key={role} className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{count}</div>
                  <div className="text-sm text-gray-600">{USER_ROLES[role]}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;