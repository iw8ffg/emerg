import React, { useState, useEffect } from 'react';

const InventoryManagement = ({ 
  token, 
  inventory, 
  setInventory, 
  inventoryFilters, 
  setInventoryFilters,
  inventoryForm,
  setInventoryForm,
  user,
  setError,
  setSuccess,
  loading,
  setLoading,
  API_BASE_URL,
  inventoryCategories = [] // Add categories prop
}) => {
  const [editingItem, setEditingItem] = useState(null);
  const [currentView, setCurrentView] = useState('list'); // list, create, edit

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

  const WarningIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
    </svg>
  );

  // Load inventory
  const loadInventory = async () => {
    if (!token) return;
    
    try {
      const params = new URLSearchParams();
      if (inventoryFilters.category) params.append('category', inventoryFilters.category);
      if (inventoryFilters.location) params.append('location', inventoryFilters.location);
      if (inventoryFilters.low_stock) params.append('low_stock', 'true');
      if (inventoryFilters.expiring_soon) params.append('expiring_soon', 'true');
      
      const response = await fetch(`${API_BASE_URL}/api/inventory?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setInventory(data);
      }
    } catch (error) {
      console.error('Failed to load inventory:', error);
    }
  };

  // Create or update inventory item
  const saveInventoryItem = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const url = editingItem 
        ? `${API_BASE_URL}/api/inventory/${editingItem.id}`
        : `${API_BASE_URL}/api/inventory`;
      
      const method = editingItem ? 'PUT' : 'POST';
      
      const itemData = {
        ...inventoryForm,
        quantity: parseInt(inventoryForm.quantity),
        min_quantity: parseInt(inventoryForm.min_quantity),
        max_quantity: inventoryForm.max_quantity ? parseInt(inventoryForm.max_quantity) : null,
        cost_per_unit: inventoryForm.cost_per_unit ? parseFloat(inventoryForm.cost_per_unit) : null,
        expiry_date: inventoryForm.expiry_date || null
      };
      
      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(itemData)
      });
      
      if (response.ok) {
        setSuccess(editingItem ? 'Articolo aggiornato con successo!' : 'Articolo creato con successo!');
        setInventoryForm({
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
        setEditingItem(null);
        setCurrentView('list');
        loadInventory();
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

  // Delete inventory item
  const deleteInventoryItem = async (itemId, itemName) => {
    if (!window.confirm(`Sei sicuro di voler eliminare "${itemName}"?`)) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/inventory/${itemId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        setSuccess('Articolo eliminato con successo!');
        loadInventory();
      } else {
        const data = await response.json();
        setError(data.detail || 'Errore durante l\'eliminazione');
      }
    } catch (error) {
      setError('Errore di connessione al server');
    }
  };

  // Start editing item
  const startEditing = (item) => {
    setInventoryForm({
      name: item.name || '',
      category: item.category || '',
      quantity: item.quantity || 0,
      unit: item.unit || 'pz',
      location: item.location || '',
      min_quantity: item.min_quantity || 0,
      max_quantity: item.max_quantity || '',
      expiry_date: item.expiry_date ? item.expiry_date.split('T')[0] : '',
      supplier: item.supplier || '',
      cost_per_unit: item.cost_per_unit || '',
      notes: item.notes || ''
    });
    setEditingItem(item);
    setCurrentView('edit');
  };

  // Get status color for quantity
  const getQuantityStatus = (item) => {
    if (item.quantity <= item.min_quantity) {
      return 'text-red-600 bg-red-100';
    } else if (item.max_quantity && item.quantity >= item.max_quantity) {
      return 'text-blue-600 bg-blue-100';
    }
    return 'text-green-600 bg-green-100';
  };

  // Get expiry status
  const getExpiryStatus = (expiryDate) => {
    if (!expiryDate) return '';
    
    const today = new Date();
    const expiry = new Date(expiryDate);
    const daysUntilExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
    
    if (daysUntilExpiry < 0) {
      return 'text-red-600 bg-red-100';
    } else if (daysUntilExpiry <= 30) {
      return 'text-orange-600 bg-orange-100';
    }
    return '';
  };

  // Filter inventory
  const filteredInventory = inventory.filter(item => {
    return true; // Filters are applied server-side
  });

  useEffect(() => {
    loadInventory();
  }, [inventoryFilters]);

  // Check permissions
  const canEdit = user && ['admin', 'coordinator', 'warehouse'].includes(user.role);
  const canDelete = user && ['admin', 'coordinator'].includes(user.role);

  if (currentView === 'create' || currentView === 'edit') {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            {currentView === 'create' ? 'Nuovo Articolo Inventario' : 'Modifica Articolo'}
          </h3>
        </div>
        <div className="px-6 py-4">
          <form onSubmit={saveInventoryItem} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nome Articolo *
                </label>
                <input
                  type="text"
                  value={inventoryForm.name}
                  onChange={(e) => setInventoryForm({ ...inventoryForm, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Categoria *
                </label>
                <select
                  value={inventoryForm.category}
                  onChange={(e) => setInventoryForm({ ...inventoryForm, category: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Seleziona categoria</option>
                  {inventoryCategories.map((category) => (
                    <option key={category.id} value={category.name}>
                      {category.icon} {category.name.charAt(0).toUpperCase() + category.name.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quantità *
                </label>
                <input
                  type="number"
                  min="0"
                  value={inventoryForm.quantity}
                  onChange={(e) => setInventoryForm({ ...inventoryForm, quantity: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Unità di Misura *
                </label>
                <select
                  value={inventoryForm.unit}
                  onChange={(e) => setInventoryForm({ ...inventoryForm, unit: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="pz">Pezzi</option>
                  <option value="kg">Chilogrammi</option>
                  <option value="lt">Litri</option>
                  <option value="mt">Metri</option>
                  <option value="mq">Metri Quadri</option>
                  <option value="scatole">Scatole</option>
                  <option value="confezioni">Confezioni</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Posizione *
                </label>
                <input
                  type="text"
                  value={inventoryForm.location}
                  onChange={(e) => setInventoryForm({ ...inventoryForm, location: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="es. Magazzino A, Scaffale 2, Piano 1"
                  required
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quantità Minima (Alert)
                </label>
                <input
                  type="number"
                  min="0"
                  value={inventoryForm.min_quantity}
                  onChange={(e) => setInventoryForm({ ...inventoryForm, min_quantity: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Quantità Massima (Opzionale)
                </label>
                <input
                  type="number"
                  min="0"
                  value={inventoryForm.max_quantity}
                  onChange={(e) => setInventoryForm({ ...inventoryForm, max_quantity: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Data Scadenza
                </label>
                <input
                  type="date"
                  value={inventoryForm.expiry_date}
                  onChange={(e) => setInventoryForm({ ...inventoryForm, expiry_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fornitore
                </label>
                <input
                  type="text"
                  value={inventoryForm.supplier}
                  onChange={(e) => setInventoryForm({ ...inventoryForm, supplier: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Costo per Unità (€)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={inventoryForm.cost_per_unit}
                  onChange={(e) => setInventoryForm({ ...inventoryForm, cost_per_unit: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Note
              </label>
              <textarea
                value={inventoryForm.notes}
                onChange={(e) => setInventoryForm({ ...inventoryForm, notes: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Note aggiuntive, specifiche tecniche, etc."
              />
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  setCurrentView('list');
                  setEditingItem(null);
                  setInventoryForm({
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
                {loading ? 'Salvataggio...' : (currentView === 'create' ? 'Crea Articolo' : 'Aggiorna Articolo')}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  // Main inventory list view
  return (
    <div className="space-y-6">
      {/* Header with filters and actions */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">Gestione Inventario</h3>
            {canEdit && (
              <button
                onClick={() => setCurrentView('create')}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
              >
                <PlusIcon />
                <span>Nuovo Articolo</span>
              </button>
            )}
          </div>
        </div>
        
        {/* Filters */}
        <div className="px-6 py-4 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <select
              value={inventoryFilters.category}
              onChange={(e) => setInventoryFilters({ ...inventoryFilters, category: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="">Tutte le categorie</option>
              <option value="attrezzature">Attrezzature</option>
              <option value="medicinali">Medicinali</option>
              <option value="alimentari">Alimentari</option>
              <option value="vestiario">Vestiario</option>
              <option value="comunicazione">Comunicazione</option>
              <option value="energia">Energia</option>
              <option value="trasporti">Trasporti</option>
              <option value="altro">Altro</option>
            </select>
            
            <input
              type="text"
              placeholder="Filtra per posizione"
              value={inventoryFilters.location}
              onChange={(e) => setInventoryFilters({ ...inventoryFilters, location: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={inventoryFilters.low_stock}
                onChange={(e) => setInventoryFilters({ ...inventoryFilters, low_stock: e.target.checked })}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Solo scorte basse</span>
            </label>
            
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={inventoryFilters.expiring_soon}
                onChange={(e) => setInventoryFilters({ ...inventoryFilters, expiring_soon: e.target.checked })}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">In scadenza</span>
            </label>
          </div>
        </div>
      </div>
      
      {/* Inventory items */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4">
          {filteredInventory.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              Nessun articolo trovato
            </p>
          ) : (
            <div className="space-y-4">
              {filteredInventory.map((item) => (
                <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h4 className="font-medium text-gray-900">{item.name}</h4>
                        <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                          {item.category}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded-full ${getQuantityStatus(item)}`}>
                          {item.quantity} {item.unit}
                        </span>
                        {item.expiry_date && (
                          <span className={`px-2 py-1 text-xs rounded-full ${getExpiryStatus(item.expiry_date)}`}>
                            Scad: {new Date(item.expiry_date).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                      
                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-2 text-sm text-gray-600">
                        <div><strong>Posizione:</strong> {item.location}</div>
                        <div><strong>Min:</strong> {item.min_quantity}</div>
                        {item.supplier && <div><strong>Fornitore:</strong> {item.supplier}</div>}
                        {item.cost_per_unit && <div><strong>Costo:</strong> €{item.cost_per_unit}</div>}
                      </div>
                      
                      {item.notes && (
                        <p className="text-sm text-gray-600 mt-2">{item.notes}</p>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {item.quantity <= item.min_quantity && (
                        <WarningIcon className="h-5 w-5 text-red-500" />
                      )}
                      
                      {canEdit && (
                        <button
                          onClick={() => startEditing(item)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-md"
                        >
                          <EditIcon />
                        </button>
                      )}
                      
                      {canDelete && (
                        <button
                          onClick={() => deleteInventoryItem(item.id, item.name)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-md"
                        >
                          <DeleteIcon />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InventoryManagement;