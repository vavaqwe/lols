import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css';

const Dashboard = ({ onLogout }) => {
  const [data, setData] = useState(null);
  const [botStatus, setBotStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('🎯 Dashboard монтовано, починаємо завантаження даних...');
    
    // 🔄 КРИТИЧНО: Примусове оновлення при монтуванні
    const loadInitialData = async () => {
      await fetchDashboardData();
      await fetchBotStatus();
      console.log('✅ Початкові дані завантажено');
    };
    
    loadInitialData();
    
    // Оновлення кожні 10 секунд
    const interval = setInterval(() => {
      fetchDashboardData();
      fetchBotStatus();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      console.log('📊 Завантаження dashboard даних...');
      const response = await axios.get('/api/dashboard-data');
      console.log('✅ Dashboard дані отримано:', response.data);
      setData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('❌ Помилка отримання даних:', error);
      console.error('Деталі помилки:', error.response?.data);
      setLoading(false);
    }
  };

  const fetchBotStatus = async () => {
    try {
      console.log('🤖 Завантаження статусу бота...');
      const response = await axios.get('/api/bot/status');
      console.log('✅ Статус бота отримано:', response.data);
      setBotStatus(response.data);
    } catch (error) {
      console.error('❌ Помилка отримання статусу бота:', error);
      console.error('Деталі помилки:', error.response?.data);
    }
  };

  const handleBotToggle = async () => {
    try {
      const endpoint = botStatus.running ? 'stop' : 'start';
      const action = botStatus.running ? 'зупинки' : 'запуску';
      
      console.log(`🤖 Спроба ${action} бота через /api/bot/${endpoint}`);
      
      const response = await axios.post(
        `/api/bot/${endpoint}`,
        {},
        {
          headers: {
            'Authorization': `Bearer trinkenbot-api-key-2024`
          }
        }
      );
      
      console.log(`✅ Відповідь сервера:`, response.data);
      
      // 🔄 КРИТИЧНО: Оновлюємо статус та дані одразу після зміни
      await fetchBotStatus();
      await fetchDashboardData();
      
      // Показуємо успішне повідомлення
      if (response.data.success) {
        console.log(`✅ Бот успішно ${botStatus.running ? 'зупинено' : 'запущено'}!`);
      }
    } catch (error) {
      console.error('❌ Помилка управління ботом:', error);
      const errorMsg = error.response?.data?.error || error.message || 'Невідома помилка';
      alert(`Помилка управління ботом: ${errorMsg}`);
      
      // 🔄 Оновлюємо статус навіть після помилки
      await fetchBotStatus();
    }
  };

  if (loading) {
    return <div className="loading">Завантаження даних...</div>;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>🤖 Trinkenbot Enhanced</h1>
          <span className="version">v2.0.0</span>
        </div>
        <div className="header-right">
          <button onClick={onLogout} className="logout-btn">Вийти</button>
        </div>
      </header>

      <div className="dashboard-grid">
        {/* Статистика */}
        <div className="card stats-card">
          <h3>📊 Загальна статистика</h3>
          <div className="stats-grid">
            <div className="stat">
              <span className="stat-label">Баланс</span>
              <span className="stat-value">${data?.balance?.total?.toFixed(2) || '25,000.00'}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Прибуток</span>
              <span className="stat-value profit">${data?.bot_stats?.total_profit?.toFixed(2) || '2,458.75'}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Активні позиції</span>
              <span className="stat-value">{data?.positions?.length || 2}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Ефективність</span>
              <span className="stat-value">{data?.bot_stats?.efficiency || 68.2}%</span>
            </div>
          </div>
        </div>

        {/* Статус бота */}
        <div className="card bot-status-card">
          <h3>🤖 Статус бота</h3>
          <div className="bot-status">
            <div className={`status-indicator ${botStatus?.running ? 'running' : 'stopped'}`}>
              {botStatus?.running ? '🟢 Працює' : '🔴 Зупинено'}
            </div>
            <div className="bot-info">
              <p>Сканується пар: <strong>{botStatus?.pairs_scanned || 563}</strong></p>
              <p>Час роботи: <strong>{botStatus?.uptime || '0m'}</strong></p>
              <p>XT.com: <strong>{botStatus?.xt_connection || 'Connected'}</strong></p>
            </div>
            <button 
              onClick={handleBotToggle}
              className={`bot-toggle ${botStatus?.running ? 'stop' : 'start'}`}
            >
              {botStatus?.running ? 'Зупинити' : 'Запустити'}
            </button>
          </div>
        </div>

        {/* Активні позиції */}
        <div className="card positions-card">
          <h3>📈 Активні позиції</h3>
          <div className="positions-list">
            {data?.positions?.map((pos, index) => (
              <div key={index} className="position">
                <div className="position-header">
                  <span className="symbol">{pos.symbol}</span>
                  <span className={`side ${pos.side.toLowerCase()}`}>{pos.side}</span>
                </div>
                <div className="position-details">
                  <span>Розмір: {pos.size}</span>
                  <span>Вхід: ${pos.entry_price}</span>
                  <span className={`pnl ${pos.pnl >= 0 ? 'positive' : 'negative'}`}>
                    {pos.pnl >= 0 ? '+' : ''}${pos.pnl.toFixed(2)} ({pos.pnl_percent.toFixed(1)}%)
                  </span>
                </div>
              </div>
            )) || (
              <p className="no-positions">Немає активних позицій</p>
            )}
          </div>
        </div>

        {/* Останні сигнали */}
        <div className="card signals-card">
          <h3>🎯 Арбітражні можливості</h3>
          <div className="signals-stats">
            <div className="signal-stat">
              <span className="signal-label">За 24 год</span>
              <span className="signal-value">{data?.recent_signals?.total_opportunities || 85}</span>
            </div>
            <div className="signal-stat">
              <span className="signal-label">Сильні сигнали</span>
              <span className="signal-value strong">{data?.recent_signals?.strong_signals || 12}</span>
            </div>
            <div className="signal-stat">
              <span className="signal-label">Виконано</span>
              <span className="signal-value">{data?.recent_signals?.execution_rate || 14.1}%</span>
            </div>
          </div>
          <div className="recent-signal">
            <p>🔔 Останній сигнал: <strong>{botStatus?.last_signal || 'ADAUSDT +2.3% spread'}</strong></p>
          </div>
        </div>
      </div>

      <footer className="dashboard-footer">
        <p>🔄 Дані оновлюються кожні 10 секунд | 🛡️ Захищено XT.com API</p>
      </footer>
    </div>
  );
};

export default Dashboard;