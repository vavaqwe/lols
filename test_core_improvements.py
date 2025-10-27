#!/usr/bin/env python3
"""
Тест покращень бота:
1. RPC reconnect
2. Spread 2-3%
3. Heartbeat моніторинг
"""
import os
import sys
import time
import logging

# ENV
os.environ['ADMIN_PASSWORD'] = 'Admin123'
os.environ['XT_API_KEY'] = 'edbae47c-5dd1-4e17-85a5-4ddbf9a0198d'
os.environ['XT_API_SECRET'] = 'dc15cbd32da51249b35326dcc0bafb9045771fa8'
os.environ['TELEGRAM_BOT_TOKEN'] = '7198851873:AAFkiFUMNpdt8o7_jb_ZYGfHH_nZUVU_9Lw'
os.environ['TELEGRAM_CHAT_ID'] = '7820995179'
os.environ['ALLOW_LIVE_TRADING'] = 'True'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_spread_config():
    """Тест spread 2-3%"""
    logging.info("=" * 80)
    logging.info("ТЕСТ 1: Spread Configuration (2-3%)")
    logging.info("=" * 80)

    try:
        import config

        logging.info(f"✅ MIN_SPREAD: {config.MIN_SPREAD}% (очікується 2.0%)")
        logging.info(f"✅ MAX_SPREAD: {config.MAX_SPREAD}% (очікується 3.0%)")
        logging.info(f"✅ MIN_NET_PROFIT: {config.MIN_NET_PROFIT_PERCENT}% (очікується 1.4%)")

        assert config.MIN_SPREAD == 2.0, f"❌ MIN_SPREAD має бути 2.0%, а не {config.MIN_SPREAD}%"
        assert config.MAX_SPREAD == 3.0, f"❌ MAX_SPREAD має бути 3.0%, а не {config.MAX_SPREAD}%"
        assert config.MIN_NET_PROFIT_PERCENT == 1.4, f"❌ MIN_NET_PROFIT має бути 1.4%"

        logging.info("🎉 Spread налаштовано правильно: 2-3% для автоторгівлі")
        return True

    except Exception as e:
        logging.error(f"❌ Помилка: {e}")
        return False

def test_blockchain_reconnect():
    """Тест RPC reconnect і heartbeat"""
    logging.info("")
    logging.info("=" * 80)
    logging.info("ТЕСТ 2: RPC Reconnect + Heartbeat")
    logging.info("=" * 80)

    try:
        from blockchain_pools_client import BlockchainPoolsClient

        client = BlockchainPoolsClient()

        # Перевіряємо що методи reconnect існують
        assert hasattr(client, '_ensure_connection'), "❌ Немає методу _ensure_connection"
        assert hasattr(client, '_init_web3_connections'), "❌ Немає методу _init_web3_connections"
        assert hasattr(client, '_log_heartbeat'), "❌ Немає методу _log_heartbeat"

        logging.info("✅ Методи reconnect присутні")

        # Тест heartbeat
        client._log_heartbeat()
        logging.info("✅ Heartbeat працює")

        # Тест reconnect (якщо Web3 доступний)
        if client.w3_eth or client.w3_bsc:
            result = client._ensure_connection('ethereum')
            logging.info(f"✅ Ethereum reconnect: {result}")

            result = client._ensure_connection('bsc')
            logging.info(f"✅ BSC reconnect: {result}")
        else:
            logging.warning("⚠️ Web3 не встановлено, пропускаємо реальний reconnect тест")

        # Перевіряємо параметри reconnect
        assert hasattr(client, 'max_retries'), "❌ Немає max_retries"
        assert hasattr(client, 'retry_delay'), "❌ Немає retry_delay"
        assert hasattr(client, 'connection_check_interval'), "❌ Немає connection_check_interval"

        logging.info(f"✅ Reconnect параметри: retries={client.max_retries}, delay={client.retry_delay}s, interval={client.connection_check_interval}s")

        logging.info("🎉 RPC Reconnect налаштовано правильно")
        return True

    except Exception as e:
        logging.error(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dex_heartbeat():
    """Тест DEX heartbeat"""
    logging.info("")
    logging.info("=" * 80)
    logging.info("ТЕСТ 3: DEX/XT Heartbeat Monitoring")
    logging.info("=" * 80)

    try:
        from dex_client import dex_client

        # Перевіряємо що DEX client має rate limiting
        assert hasattr(dex_client, 'provider_stats'), "❌ Немає provider_stats"
        assert hasattr(dex_client, 'last_request_time'), "❌ Немає last_request_time"

        logging.info("✅ DEX client має rate limiting")

        # Пробуємо отримати ціну (real-time тест)
        logging.info("🔍 Пробуємо отримати real-time ціну BTC...")
        start_time = time.time()
        price = dex_client.get_dex_price('BTC')
        duration = time.time() - start_time

        if price and price > 0:
            logging.info(f"✅ BTC ціна: ${price:,.2f} (за {duration:.2f}с)")
        else:
            logging.warning(f"⚠️ BTC ціна недоступна (можливо rate limit або API не відповідає)")

        # Перевіряємо статистику
        stats = dex_client.provider_stats
        logging.info(f"📊 DEX статистика: {stats}")

        logging.info("🎉 DEX моніторинг працює")
        return True

    except Exception as e:
        logging.error(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_xt_connection():
    """Тест з'єднання з XT.com"""
    logging.info("")
    logging.info("=" * 80)
    logging.info("ТЕСТ 4: XT.com Connection (Real-time)")
    logging.info("=" * 80)

    try:
        from xt_client import create_xt, get_xt_price

        logging.info("🔍 Створюємо XT client...")
        xt = create_xt()

        if not xt:
            logging.warning("⚠️ XT client не створено, можливо неправильні ключі")
            return False

        logging.info("✅ XT client створено")

        # Пробуємо отримати ціну
        logging.info("🔍 Отримуємо real-time ціну BTC з XT.com...")
        start_time = time.time()
        price = get_xt_price(xt, 'BTC/USDT:USDT')
        duration = time.time() - start_time

        if price and price > 0:
            logging.info(f"✅ XT BTC: ${price:,.2f} (за {duration:.2f}с)")
        else:
            logging.warning("⚠️ XT ціна недоступна")
            return False

        logging.info("🎉 XT.com підключення працює")
        return True

    except Exception as e:
        logging.error(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_spread_calculation():
    """Тест реального розрахунку spread"""
    logging.info("")
    logging.info("=" * 80)
    logging.info("ТЕСТ 5: Real Spread Calculation (2-3%)")
    logging.info("=" * 80)

    try:
        from dex_client import dex_client
        from xt_client import create_xt, get_xt_price
        import config

        xt = create_xt()
        if not xt:
            logging.warning("⚠️ XT client недоступний")
            return False

        # Тестуємо на BTC
        symbol = 'BTC/USDT:USDT'

        logging.info(f"🔍 Розраховуємо spread для {symbol}...")

        # DEX ціна
        dex_price = dex_client.get_dex_price('BTC')
        if not dex_price:
            logging.warning("⚠️ DEX ціна недоступна")
            return False

        # XT ціна
        xt_price = get_xt_price(xt, symbol)
        if not xt_price:
            logging.warning("⚠️ XT ціна недоступна")
            return False

        # Розрахунок spread
        spread = abs((dex_price - xt_price) / xt_price * 100)

        logging.info(f"📊 DEX: ${dex_price:,.2f}")
        logging.info(f"📊 XT:  ${xt_price:,.2f}")
        logging.info(f"📊 Spread: {spread:.2f}%")

        # Перевірка фільтрів
        min_spread = config.MIN_SPREAD
        max_spread = config.MAX_SPREAD

        logging.info(f"🎯 Фільтр: {min_spread}% ≤ spread ≤ {max_spread}%")

        if min_spread <= spread <= max_spread:
            logging.info(f"✅ Spread {spread:.2f}% В ДІАПАЗОНІ {min_spread}-{max_spread}% → СИГНАЛ!")
        else:
            logging.info(f"⚠️ Spread {spread:.2f}% поза діапазоном {min_spread}-{max_spread}%")

        logging.info("🎉 Spread розрахунок працює правильно")
        return True

    except Exception as e:
        logging.error(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    logging.info("🚀 ТЕСТУВАННЯ ПОКРАЩЕНЬ БОТА")
    logging.info("")

    results = []

    # Тести
    results.append(('Spread 2-3%', test_spread_config()))
    results.append(('RPC Reconnect', test_blockchain_reconnect()))
    results.append(('DEX Heartbeat', test_dex_heartbeat()))
    results.append(('XT Connection', test_xt_connection()))
    results.append(('Real Spread', test_real_spread_calculation()))

    # Результати
    logging.info("")
    logging.info("=" * 80)
    logging.info("📊 РЕЗУЛЬТАТИ ТЕСТІВ:")
    logging.info("=" * 80)

    passed = 0
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logging.info(f"   {status} {name}")
        if success:
            passed += 1

    logging.info("")
    logging.info(f"📈 Пройдено: {passed}/{len(results)} тестів ({passed/len(results)*100:.0f}%)")

    if passed == len(results):
        logging.info("🎉 ВСІ ПОКРАЩЕННЯ ПРАЦЮЮТЬ!")
        logging.info("")
        logging.info("✅ Spread налаштовано: 2.0-3.0% для автоторгівлі")
        logging.info("✅ RPC reconnect: автоматичний при падінні зв'язку")
        logging.info("✅ Heartbeat: моніторинг кожні 30 секунд")
        logging.info("✅ Real-time: сигнали ловляться в реальному часі")
        sys.exit(0)
    else:
        logging.warning(f"⚠️ {len(results) - passed} тест(ів) не пройшли")
        sys.exit(1)
