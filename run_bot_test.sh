#!/bin/bash

# ENV variables
export ADMIN_PASSWORD='Admin123'
export XT_API_KEY='edbae47c-5dd1-4e17-85a5-4ddbf9a0198d'
export XT_API_SECRET='dc15cbd32da51249b35326dcc0bafb9045771fa8'
export TELEGRAM_BOT_TOKEN='7198851873:AAFkiFUMNpdt8o7_jb_ZYGfHH_nZUVU_9Lw'
export TELEGRAM_CHAT_ID='7820995179'
export TELEGRAM_ADMIN_2_ID='716108244'
export TELEGRAM_GROUP_CHAT_ID='-1002749740706'
export XT_ACCOUNT_2_API_KEY='1db94939-6267-449d-8a2f-4cfd5d16f0af'
export XT_ACCOUNT_2_API_SECRET='fe6172badbc263cbbda6bbc451373b6eba16a4bb'
export ALLOW_LIVE_TRADING='True'
export PORT='5000'

echo "🚀 Запуск бота в тестовому режимі (30 секунд)..."
echo "📊 Конфігурація:"
echo "   MIN_SPREAD: 2.0%"
echo "   MAX_SPREAD: 3.0%"
echo "   Heartbeat: кожні 30с"
echo "   Reconnect: автоматичний"
echo ""

timeout 30 python3 main.py 2>&1 | tee bot_test_output.log &
PID=$!

echo "🔍 Моніторимо запуск (PID: $PID)..."
sleep 5

# Перевіряємо чи процес живий
if ps -p $PID > /dev/null; then
    echo "✅ Бот успішно запущено!"
    echo ""
    echo "📝 Перші 50 рядків логу:"
    head -50 bot_test_output.log
    
    # Чекаємо закінчення
    wait $PID
    EXIT_CODE=$?
    
    echo ""
    echo "🏁 Бот завершено (exit code: $EXIT_CODE)"
    
    # Аналіз логу
    echo ""
    echo "📊 Аналіз логу:"
    echo "   Heartbeat сигналів: $(grep -c 'heartbeat' bot_test_output.log || echo 0)"
    echo "   RPC запитів: $(grep -c 'Ethereum\|BSC\|Solana' bot_test_output.log || echo 0)"
    echo "   Знайдені сигнали: $(grep -c 'СИГНАЛ\|SIGNAL' bot_test_output.log || echo 0)"
    echo "   Помилки: $(grep -c 'ERROR\|❌' bot_test_output.log || echo 0)"
    echo "   Reconnect: $(grep -c 'reconnect\|RECONNECT' bot_test_output.log || echo 0)"
    
else
    echo "❌ Бот не запустився або завершився передчасно"
    echo "📝 Лог помилок:"
    cat bot_test_output.log
    exit 1
fi
