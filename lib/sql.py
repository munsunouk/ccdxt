# # Aurota DB Connection
import mysql.connector
import json
from functools import wraps
import logging
import datetime
import time

from mars.base.utils.errors import TooManyTriesException
class Sql:

    def __init__(self, config) -> None:
        
        self.retries = 5
        self.retriesTime = 60
        self.config = config
        
        self.connect_db(self.config)
        
    def retry(method):
        '''
        retry method on certain time
        '''
        
        @wraps(method)
        def retry_method(self, *args, **kwargs):
            for i in range(self.retries):
                
                try:
                    return method(self, *args, **kwargs)
                except Exception:
                    if i == self.retries - 1:
                        raise TooManyTriesException(method)
                    else :
                        logging.warning('{} - {} - {} - Attempt {}'.format(datetime.datetime.now(), method.__name__, (args, kwargs), i))
                        time.sleep(self.retriesTime)
                        self.connect_db(self.config)

        return retry_method

    def connect_db(self, config):
        
        self._conn = mysql.connector.connect(
            host=config['endpoint'],
            user=config['user'],
            passwd=config['password'],
            port=config['port'],
            database=config['db_name']
        )
        
        self._cur = self._conn.cursor()
        
    @retry
    def select_db(self, table):
            
        query = f"SELECT *\
                    FROM({table})"
                    
        self._cur.execute(query)
        
        query_results = self._cur.fetchall()
        
        return query_results
    
    # @retry
    def insert_db(self, data_list) :
        
        for data in data_list :
            
            table = data['table']
            values = str(data['values']).replace("'", "")
            
            query = f"INSERT INTO"\
                    f"{table}"\
                    f"{values}"\
                    f"VALUES"\
                    f"{values}"\
                        
            self._cur.execute(query)
            
            self._conn.commit()
        
    @retry
    def insert_balance(self,
                       market_code,
                       account_code,
                       assets: dict,
                       raw_response: dict):

        sql = '''
                INSERT INTO PV_BALANCE_CEFI_H (market_code, account_code, assets, raw_response)
                VALUES(%s, %s, %s, %s)
              '''
              
        self._cur.execute(sql, (market_code, account_code, json.dumps(assets), json.dumps(raw_response)))

        self._conn.commit()

    @retry
    def insert_tx(self, data, market_id, strategy_id, group_id):
        
        result = {
            'market_code' : market_id,
            'strategy_id' : strategy_id,
            'group_id' : group_id,
        }
        
        data.update(result)
        
        sql = '''
                INSERT INTO PV_TRADE_DEFI_H \
                    (market_code, strategy_id, group_id, function_name, tx_hash, from_network, \
                        to_network, token_in, token_out, amount_in, amount_out, from_address, \
                            to_address, status_type, gas_fee)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              '''
              
        self._cur.execute(sql, (
            data['market_code'],
            data['strategy_id'],
            data['group_id'],
            data['function'],
            data['tx_hash'],
            data['from_network'],
            data['to_network'],
            data['token_in'],
            data['token_out'],
            data['amount_in'],
            data['amount_out'],
            data['from_address'],
            data['to_address'],
            data['status'],
            data['gas_fee'],
            )
        )

        self._conn.commit()
        
    @retry
    def insert_pool_tx(self, data, market_id, strategy_id, group_id):
        
        result = {
            'market_code' : market_id,
            'strategy_id' : strategy_id,
            'group_id' : group_id,
        }
        
        data.update(result)
        
        sql = '''
                INSERT INTO PV_TRADE_POOL_H \
                    (market_code, strategy_id, group_id, function_name, tx_hash, pool_name, \
                    pool_address, input, address, gas_fee) \
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              '''
              
        self._cur.execute(sql, (
            data['market_code'],
            data['strategy_id'],
            data['group_id'],
            data['function'],
            data['tx_hash'],
            data['pool_name'],
            data['pool_address'],
            data['input'],
            data['address'],
            data['status'],
            data['gas_fee'],
            )
        )

        self._conn.commit()
        
        
    @retry
    def get_defi_balance_data(self, date, next_date, market_ids, account_ids, reverse=True) :
        
        if reverse :

            sql = '''
                    SELECT T1.account_code, T1.market_code, T1.assets, T1.created_at
                    FROM TRADE_DATA.PV_BALANCE_CEFI_H T1
                    INNER JOIN (
                        SELECT account_code, market_code, MAX(created_at) AS latest_datetime
                        FROM TRADE_DATA.PV_BALANCE_CEFI_H
                        WHERE created_at >= '%s' AND created_at < '%s'
                        AND market_code IN %s
                        AND account_code IN %s
                        GROUP BY market_code
                    ) T2
                    ON T1.market_code = T2.market_code AND T1.created_at = T2.latest_datetime AND T1.account_code = T2.account_code
                    ORDER BY T1.market_code
                    DESC
                '''% (
                    date,
                    next_date,
                    market_ids,
                    account_ids
                )
                
        else :
            
            sql = '''
                    SELECT T1.account_code, T1.market_code, T1.assets, T1.created_at
                    FROM TRADE_DATA.PV_BALANCE_CEFI_H T1
                    INNER JOIN (
                        SELECT account_code, market_code, MAX(created_at) AS latest_datetime
                        FROM TRADE_DATA.PV_BALANCE_CEFI_H
                        WHERE created_at >= '%s' AND created_at < '%s'
                        AND market_code IN %s
                        AND account_code IN %s
                        GROUP BY market_code
                    ) T2
                    ON T1.market_code = T2.market_code AND T1.created_at = T2.latest_datetime AND T1.account_code = T2.account_code
                    ORDER BY T1.market_code, T1.account_code
                '''% (
                    date,
                    next_date,
                    market_ids,
                    account_ids
                )
              
        self._cur.execute(sql)
        query_results = self._cur.fetchall()
        
        return query_results
    
    @retry
    def get_fixing_data(self, date, next_date, market_name=None):
        
        if market_name :
        
            sql = '''
                SELECT TA1.est_value, TA2.fixing_rates, TA1.ymd
                FROM (
                    SELECT est_value, DATE_FORMAT(T1.created,'%%Y-%%m-%%d') as ymd
                    FROM TRADE_DATA.PV_DEX_PRICE_H T1
                    INNER JOIN (
                        SELECT market_name, MAX(created) as latest_datetime
                        FROM TRADE_DATA.PV_DEX_PRICE_H
                        WHERE created >= '%s' AND created < '%s'
                            AND market_name = '%s'
                    ) T2
                    ON T1.market_name = T2.market_name AND T1.created = T2.latest_datetime
                ) TA1
                INNER JOIN (
                    SELECT fixing_rates, DATE_FORMAT(T3.created_at,'%%Y-%%m-%%d') as ymd
                    FROM TRADE_DATA.PV_FIXINGRATE_H T3
                    INNER JOIN (
                        SELECT MAX(created_at) as latest_datetime
                        FROM TRADE_DATA.PV_FIXINGRATE_H
                        WHERE created_at >= '%s' AND created_at < '%s'
                    ) T4
                    ON T3.created_at = T4.latest_datetime
                ) TA2
                ON TA1.ymd = TA2.ymd
                '''% (
                    date,
                    next_date,
                    market_name,
                    date,
                    next_date
                )
            
            self._cur.execute(sql)
            query_results = self._cur.fetchall()
                
        else :
            
            sql = '''
                SELECT fixing_rates, DATE_FORMAT(T3.created_at,'%%Y-%%m-%%d') as ymd
                FROM TRADE_DATA.PV_FIXINGRATE_H T3
                INNER JOIN (
                    SELECT MAX(created_at) as latest_datetime
                    FROM TRADE_DATA.PV_FIXINGRATE_H
                    WHERE created_at >= '%s' AND created_at < '%s'
                ) T4
                ON T3.created_at = T4.latest_datetime
                '''% (
                    date,
                    next_date
                )

            self._cur.execute(sql)
            query_results = self._cur.fetchall()
            query_results.insert(1,1)
        
        return query_results
    
    @retry
    def get_defi_volumn(self, date, next_date, strategy_id, volume_coins) :
        
        sql = '''
            SELECT (
                SUM(CASE WHEN token_in = '%s' THEN amount_in ELSE 0 END) +
                SUM(CASE WHEN token_out = '%s' THEN amount_out ELSE 0 END) +
                SUM(CASE WHEN token_in = '%s' THEN amount_in ELSE 0 END) +
                SUM(CASE WHEN token_out = '%s' THEN amount_out ELSE 0 END)
                ) AS volume_tokenA,
                SUM(CASE WHEN token_in = '%s' THEN amount_in ELSE 0 END) +
                SUM(CASE WHEN token_out = '%s' THEN amount_out ELSE 0 END) +
                SUM(CASE WHEN token_in = '%s' THEN amount_in ELSE 0 END) +
                SUM(CASE WHEN token_out = '%s' THEN amount_out ELSE 0 END) AS volume_tokenB,
                SUM(CASE WHEN status_type = 1 THEN status_type ELSE 0 END) as volumn_tx,
                SUM(gas_fee) AS gas_fee
            FROM TRADE_DATA.PV_TRADE_DEFI_H
            WHERE created_at >= '%s' AND created_at <'%s' AND strategy_id = '%s'
            '''% (
                str(volume_coins[0][0]),
                str(volume_coins[0][0]),
                str(volume_coins[0][1]),
                str(volume_coins[0][1]),
                str(volume_coins[1][0]),
                str(volume_coins[1][0]),
                str(volume_coins[1][1]),
                str(volume_coins[1][1]),
                date,
                next_date,
                strategy_id
            )
        
        self._cur.execute(sql)
        query_results = self._cur.fetchall()
        
        return query_results
    
    @retry
    def get_defi_txPnl(self, date, next_date, strategy_id, except_tx_ids) :
        
        sql = '''
            SELECT SUM(t.amount_out - lag.amount_in) as profit
            FROM (
                SELECT *
                FROM TRADE_DATA.PV_TRADE_DEFI_H 
                WHERE group_id NOT IN %s
            ) t
            JOIN (
            SELECT seq, amount_in, gas_fee, token_in, token_out, group_id
            FROM TRADE_DATA.PV_TRADE_DEFI_H
            WHERE group_id NOT IN %s
            ) lag ON t.seq = lag.seq + 1 AND t.group_id = lag.group_id
            WHERE created_at >= '%s' AND created_at < '%s' AND strategy_id = '%s'
            '''% (
                except_tx_ids,
                except_tx_ids,
                date,
                next_date,
                strategy_id,
            )
        
        self._cur.execute(sql)
        query_results = self._cur.fetchall()
        
        return query_results
    
    # @retry
    def store_tokenDiff(self, *args, **kwargs) :
              
        keys = str(tuple(kwargs.keys())).replace("'", "")
        values = str(tuple(kwargs.values()))
        
        query = f"\
                INSERT INTO \
                sys.token_diff{keys} \
                VALUES{values} \
                "

        self._cur.execute(query)
        
        self._conn.commit()
        
    @retry
    def get_defi_txPnl(self, date, next_date, strategy_id, except_tx_ids) :
        
        sql = '''
            SELECT SUM(t.amount_out - lag.amount_in) as profit
            FROM (
                SELECT *
                FROM TRADE_DATA.PV_TRADE_DEFI_H 
                WHERE group_id NOT IN %s
            ) t
            JOIN (
            SELECT seq, amount_in, gas_fee, token_in, token_out, group_id
            FROM TRADE_DATA.PV_TRADE_DEFI_H
            WHERE group_id NOT IN %s
            ) lag ON t.seq = lag.seq + 1 AND t.group_id = lag.group_id
            WHERE created_at >= '%s' AND created_at < '%s' AND strategy_id = '%s'
            '''% (
                except_tx_ids,
                except_tx_ids,
                date,
                next_date,
                strategy_id,
            )
        
        self._cur.execute(sql)
        query_results = self._cur.fetchall()
        
        return query_results