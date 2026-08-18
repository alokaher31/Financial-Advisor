/**
 * Banner that displays when the app is running on mock data.
 * Alerts users that they're not connected to the real backend.
 */

const USE_MOCK_DATA =
  String(import.meta.env.VITE_USE_MOCK_DATA ?? 'true').toLowerCase() !== 'false';

export function MockDataBanner() {
  if (!USE_MOCK_DATA) {
    return null;
  }

  return (
    <div
      style={{
        backgroundColor: '#ff9800',
        color: '#ffffff',
        padding: '12px 20px',
        textAlign: 'center',
        fontWeight: '600',
        fontSize: '14px',
        position: 'sticky',
        top: 0,
        zIndex: 9999,
        boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
      }}
    >
      <span style={{ fontSize: '18px' }}>⚠️</span>
      <span>
        Running on <strong>MOCK DATA</strong> — Backend not connected
      </span>
      <span style={{ fontSize: '18px' }}>⚠️</span>
    </div>
  );
}
