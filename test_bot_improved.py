#!/usr/bin/env python3
"""Тест покращеного бота з async та reconnect"""
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_blockchain_client():
    """Тест blockchain клієнта з reconnect"""
    try:
        from blockchain_pools_client import BlockchainPoolsClient
        
        client = BlockchainPoolsClient()
        
        # Тест heartbeat
        logging.info("🧪 Тест heartbeat...")
        client._log_heartbeat()
        
        # Тест з'єднання
        logging.info("🧪 Тест з'єднання Ethereum...")
        result = client._ensure_connection('ethereum')
        logging.info(f"   Ethereum: {result}")
        
        logging.info("🧪 Тест з'єднання BSC...")
        result = client._ensure_connection('bsc')
        logging.info(f"   BSC: {result}")
        
        # Тест отримання ціни
        logging.info("🧪 Тест отримання ціни BTC...")
        price = client.get_token_price('BTC')
        if price:
            logging.info(f"   ✅ BTC: ${price:.2f}")
        else:
            logging.warning("   ⚠️ BTC ціна недоступна (можливо Web3 не встановлено)")
        
        # Статистика
        stats = client.get_stats()
        logging.info(f"📊 Статистика: {stats['total_requests']} запитів, {stats['success_rate_percent']:.1f}% успіх")
        
        return True
    except Exception as e:
        logging.error(f"❌ Помилка blockchain client: {e}")
        return False

def test_async_wrapper():
    """Тест async wrapper"""
    try:
        import asyncio
        from dex_async import batch_fetch_spreads
        from dex_client import dex_client
        from xt_client import create_xt
        
        logging.info("🧪 Тест async wrapper...")
        
        xt = create_xt()
        if not xt:
            logging.warning("   ⚠️ XT client недоступний, пропускаємо async тест")
            return True
        
        # Тест з 3 символами
        symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'BNB/USDT:USDT']
        
        async def run_test():
            start = time.time()
            results = await batch_fetch_spreads(symbols, dex_client, xt)
            duration = time.time() - start
            
            logging.info(f"   ⚡ Отримано {len(results)} результатів за {duration:.2f}с")
            for r in results:
                logging.info(f"   {r['symbol']}: спред {r['spread_abs']:.2f}%")
            
            return len(results) > 0
        
        result = asyncio.run(run_test())
        return result
        
    except Exception as e:
        logging.error(f"❌ Помилка async wrapper: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Тест нових config значень"""
    try:
        import config
        
        logging.info("🧪 Тест config...")
        logging.info(f"   MIN_SPREAD: {config.MIN_SPREAD}% (має бути 2.0%)")
        logging.info(f"   MAX_SPREAD: {config.MAX_SPREAD}% (має бути 3.0%)")
        logging.info(f"   MIN_NET_PROFIT: {config.MIN_NET_PROFIT_PERCENT}% (має бути 1.4%)")
        
        assert config.MIN_SPREAD == 2.0, f"MIN_SPREAD має бути 2.0%, а не {config.MIN_SPREAD}%"
        assert config.MAX_SPREAD == 3.0, f"MAX_SPREAD має бути 3.0%, а не {config.MAX_SPREAD}%"
        
        logging.info("   ✅ Config правильний")
        return True
    except Exception as e:
        logging.error(f"❌ Помилка config: {e}")
        return False

if __name__ == '__main__':
    logging.info("🚀 Тестування покращеного бота...")
    logging.info("=" * 60)
    
    results = []
    
    # Тест 1: Config
    logging.info("\n📋 ТЕСТ 1: Config (spread 2-3%)")
    results.append(('Config', test_config()))
    
    # Тест 2: Blockchain client
    logging.info("\n🔗 ТЕСТ 2: Blockchain Client (reconnect + heartbeat)")
    results.append(('Blockchain', test_blockchain_client()))
    
    # Тест 3: Async wrapper
    logging.info("\n⚡ ТЕСТ 3: Async Wrapper (паралельні запити)")
    results.append(('Async', test_async_wrapper()))
    
    # Результати
    logging.info("\n" + "=" * 60)
    logging.info("📊 РЕЗУЛЬТАТИ:")
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logging.info(f"   {status} {name}")
    
    all_passed = all(r[1] for r in results)
    if all_passed:
        logging.info("\n🎉 ВСІ ТЕСТИ ПРОЙШЛИ!")
        sys.exit(0)
    else:
        logging.error("\n❌ ДЕЯКІ ТЕСТИ НЕ ПРОЙШЛИ")
        sys.exit(1)
