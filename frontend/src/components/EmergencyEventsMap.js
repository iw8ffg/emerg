import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Custom marker icons for different severity levels
const createCustomIcon = (severity) => {
  const colors = {
    'critica': '#dc2626', // red-600
    'alta': '#ea580c',    // orange-600
    'media': '#ca8a04',   // yellow-600
    'bassa': '#16a34a'    // green-600
  };
  
  const color = colors[severity] || '#6b7280'; // gray-500 as default
  
  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: ${color};
        border: 3px solid white;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 14px;
      ">!</div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15]
  });
};

const EmergencyEventsMap = ({ 
  token, 
  setError, 
  setSuccess, 
  API_BASE_URL 
}) => {
  const [mapEvents, setMapEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mapFilters, setMapFilters] = useState({
    status: 'active',
    event_type: '',
    severity: ''
  });
  const [mapCenter, setMapCenter] = useState([45.4642, 9.1900]); // Default to Milan
  const [mapZoom, setMapZoom] = useState(10);

  // Icons
  const MapIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
    </svg>
  );

  const RefreshIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>
  );

  // Load map events
  const loadMapEvents = async () => {
    if (!token) return;
    
    setLoading(true);
    try {
      const params = new URLSearchParams();
      Object.entries(mapFilters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
      
      const response = await fetch(`${API_BASE_URL}/api/events/map?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMapEvents(data.events);
        
        // Auto-fit map to show all events
        if (data.events.length > 0) {
          const bounds = data.events.map(event => [event.latitude, event.longitude]);
          const avgLat = bounds.reduce((sum, coord) => sum + coord[0], 0) / bounds.length;
          const avgLng = bounds.reduce((sum, coord) => sum + coord[1], 0) / bounds.length;
          setMapCenter([avgLat, avgLng]);
          
          // Calculate appropriate zoom level
          const latRange = Math.max(...bounds.map(b => b[0])) - Math.min(...bounds.map(b => b[0]));
          const lngRange = Math.max(...bounds.map(b => b[1])) - Math.min(...bounds.map(b => b[1]));
          const maxRange = Math.max(latRange, lngRange);
          
          let zoom = 10;
          if (maxRange > 2) zoom = 6;
          else if (maxRange > 1) zoom = 8;
          else if (maxRange > 0.5) zoom = 10;
          else if (maxRange > 0.1) zoom = 12;
          else zoom = 14;
          
          setMapZoom(zoom);
        }
        
        setSuccess(`${data.events.length} eventi caricati sulla mappa`);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Errore durante il caricamento eventi mappa');
      }
    } catch (error) {
      setError('Errore di connessione al server');
    } finally {
      setLoading(false);
    }
  };

  // Get severity color for UI elements
  const getSeverityColor = (severity) => {
    const colors = {
      'critica': 'bg-red-100 text-red-800',
      'alta': 'bg-orange-100 text-orange-800',
      'media': 'bg-yellow-100 text-yellow-800',
      'bassa': 'bg-green-100 text-green-800'
    };
    return colors[severity] || 'bg-gray-100 text-gray-800';
  };

  // Get status color
  const getStatusColor = (status) => {
    const colors = {
      'aperto': 'bg-red-100 text-red-800',
      'in_corso': 'bg-yellow-100 text-yellow-800',
      'risolto': 'bg-blue-100 text-blue-800',
      'chiuso': 'bg-green-100 text-green-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('it-IT');
  };

  // Load events on component mount and filter changes
  useEffect(() => {
    loadMapEvents();
  }, [token, mapFilters]);

  return (
    <div className="space-y-6">
      {/* Map Controls */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <MapIcon className="h-6 w-6 text-blue-600" />
              <h3 className="text-lg font-medium text-gray-900">Mappa Eventi di Emergenza</h3>
              <span className="px-3 py-1 text-sm bg-blue-100 text-blue-800 rounded-full">
                {mapEvents.length} eventi attivi
              </span>
            </div>
            <button
              onClick={loadMapEvents}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 disabled:bg-gray-400"
            >
              <RefreshIcon className={loading ? 'animate-spin' : ''} />
              <span>{loading ? 'Aggiornamento...' : 'Aggiorna'}</span>
            </button>
          </div>
        </div>
        
        {/* Filters */}
        <div className="px-6 py-4 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status Eventi
              </label>
              <select
                value={mapFilters.status}
                onChange={(e) => setMapFilters({ ...mapFilters, status: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="active">Solo Eventi Attivi</option>
                <option value="">Tutti gli Stati</option>
                <option value="aperto">Aperti</option>
                <option value="in_corso">In Corso</option>
                <option value="risolto">Risolti</option>
                <option value="chiuso">Chiusi</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tipo Evento
              </label>
              <select
                value={mapFilters.event_type}
                onChange={(e) => setMapFilters({ ...mapFilters, event_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="">Tutti i Tipi</option>
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
                value={mapFilters.severity}
                onChange={(e) => setMapFilters({ ...mapFilters, severity: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="">Tutte le Gravità</option>
                <option value="critica">Critica</option>
                <option value="alta">Alta</option>
                <option value="media">Media</option>
                <option value="bassa">Bassa</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Map Display */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4">
          {mapEvents.length === 0 ? (
            <div className="text-center py-12">
              <MapIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Nessun evento geolocalizzato</h3>
              <p className="mt-1 text-sm text-gray-500">
                Non ci sono eventi con coordinate GPS che corrispondono ai filtri selezionati.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Legend */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-sm font-medium text-gray-900 mb-3">Legenda Gravità</h4>
                <div className="flex flex-wrap gap-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 rounded-full bg-red-600"></div>
                    <span className="text-sm text-gray-700">Critica</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 rounded-full bg-orange-600"></div>
                    <span className="text-sm text-gray-700">Alta</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 rounded-full bg-yellow-600"></div>
                    <span className="text-sm text-gray-700">Media</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 rounded-full bg-green-600"></div>
                    <span className="text-sm text-gray-700">Bassa</span>
                  </div>
                </div>
              </div>
              
              {/* Map Container */}
              <div className="h-96 w-full rounded-lg overflow-hidden border border-gray-200">
                <MapContainer
                  center={mapCenter}
                  zoom={mapZoom}
                  style={{ height: '100%', width: '100%' }}
                  key={`${mapCenter[0]}-${mapCenter[1]}-${mapZoom}`}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  
                  {mapEvents.map((event) => (
                    <Marker
                      key={event.id}
                      position={[event.latitude, event.longitude]}
                      icon={createCustomIcon(event.severity)}
                    >
                      <Popup maxWidth={300} className="custom-popup">
                        <div className="p-2">
                          <h4 className="font-bold text-gray-900 mb-2">{event.title}</h4>
                          
                          <div className="space-y-2 mb-3">
                            <div className="flex flex-wrap gap-2">
                              <span className={`px-2 py-1 text-xs rounded-full ${getSeverityColor(event.severity)}`}>
                                {event.severity}
                              </span>
                              <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(event.status)}`}>
                                {event.status}
                              </span>
                              <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                                {event.event_type}
                              </span>
                            </div>
                          </div>
                          
                          <p className="text-sm text-gray-600 mb-2">{event.description}</p>
                          
                          {event.address && (
                            <p className="text-xs text-gray-500 mb-2">
                              <strong>Indirizzo:</strong> {event.address}
                            </p>
                          )}
                          
                          <div className="text-xs text-gray-500 space-y-1">
                            <p><strong>Coordinate:</strong> {event.latitude.toFixed(6)}, {event.longitude.toFixed(6)}</p>
                            <p><strong>Creato:</strong> {formatDate(event.created_at)}</p>
                            <p><strong>Operatore:</strong> {event.created_by}</p>
                          </div>
                          
                          {event.notes && (
                            <div className="mt-2 pt-2 border-t border-gray-200">
                              <p className="text-xs text-gray-600">
                                <strong>Note:</strong> {event.notes}
                              </p>
                            </div>
                          )}
                        </div>
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Events List (below map) */}
      {mapEvents.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Eventi sulla Mappa</h3>
          </div>
          <div className="px-6 py-4">
            <div className="space-y-3">
              {mapEvents.map((event) => (
                <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
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
                    <p className="text-sm text-gray-600 mt-1">{event.description}</p>
                    <div className="text-xs text-gray-500 mt-1">
                      <span>{event.latitude.toFixed(6)}, {event.longitude.toFixed(6)}</span>
                      {event.address && <span className="ml-3">{event.address}</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmergencyEventsMap;