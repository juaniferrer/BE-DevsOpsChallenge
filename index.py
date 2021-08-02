from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2
import os
import harperdb
import sys

load_dotenv()

# PostgreSQL Database credentials loaded from the .env file
DATABASE = os.getenv('DATABASE')
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')

# HarperDB Database credentials loaded from the .env file
HARPERDB_URL = os.getenv('HARPERDB_URL')
HARPERDB_USERNAME = os.getenv('HARPERDB_USERNAME')
HARPERDB_PASSWORD = os.getenv('HARPERDB_PASSWORD')

db = harperdb.HarperDB(
    url=HARPERDB_URL,
    username=HARPERDB_USERNAME,
    password=HARPERDB_PASSWORD)

app = Flask(__name__)

# CORS implemented so that we don't get errors when trying to access the server from a different server location
CORS(app)


try:
    con = psycopg2.connect(
        database=DATABASE,
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD)

    cur = con.cursor()

    # GET: Fetch users that match with login criteria
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            data = request.form.to_dict()
            print('data: ', data, file=sys.stderr)
            cur.execute("SELECT * FROM users WHERE username=%s AND userpassword =%s", (f"{data['username']}", f"{data['password']}"))
            rows = cur.fetchall()
            con.commit()
            print('rows: ', rows, file=sys.stderr)
            return jsonify(rows)

    @app.route('/developers', methods=['GET'])
    def get_developers():
            cur.execute("SELECT * FROM developers")
            rows = cur.fetchall()
            print(rows)
            return jsonify(rows)

    @app.route('/assets/all', methods=['GET'])
    def get_assets():
            cur.execute("SELECT * from assets a full outer join developer_asset d_a inner join developers d on d_a.developer_id = d.developer_id on a.asset_id = d_a.asset_id")
            rows = cur.fetchall()
            print(rows)
            return jsonify(rows)

    @app.route('/licenses/all', methods=['GET'])
    def get_licenses():
            cur.execute("SELECT * FROM licenses")
            rows = cur.fetchall()
            print(rows)
            return jsonify(rows)

    @app.route('/assets')
    def fetch_assets_by_developerId():
            developerId = request.args.get('developerId')
            cur.execute(f'SELECT * FROM developer_asset d_a INNER JOIN assets a ON d_a.asset_id = a.asset_id WHERE d_a.developer_id = \'{developerId}\'')
            rows = cur.fetchall()
            print(rows)
            return jsonify(rows)

    @app.route('/assets/freedevice')
    def free_device():
            assetId = request.args.get('assetId')
            cur.execute(f'UPDATE developer_asset SET to_date = CURRENT_DATE WHERE developer_asset.asset_id = \'{assetId}\'')
            return '200'

    @app.route('/assets/delete')
    def delete_device():
            assetId = request.args.get('assetId')
            cur.execute(f'DELETE FROM assets WHERE asset_id = \'{assetId}\'')
            return '200'

    @app.route('/assets/add', methods=['GET', 'POST'])
    def add_asset():
        if request.method == 'POST':
            data = request.form.to_dict()
            print('data: ', data, file=sys.stderr)
            cur.execute("SELECT asset_id FROM assets ORDER BY asset_id DESC LIMIT 1")
            lastAssetId = cur.fetchall()[0][0]
            lastAssetDigit = int(lastAssetId[len(lastAssetId) -1]) + 1
            newAssetId = lastAssetId[:-1]+str(lastAssetDigit)
            cur.execute("INSERT INTO assets (asset_id, brand, model, assettype, imgurl) VALUES (%s, %s, %s, %s, %s)",
                        (f"{newAssetId}", f"{data['brand']}", data['model'], f"{data['assettype']}",
                         f"{data['imgurl']}"))
            con.commit()
            return '200'

    @app.route('/developers/add', methods=['GET', 'POST'])
    def add_developer():
        if request.method == 'POST':
            data = request.form.to_dict()
            print('data: ', data, file=sys.stderr)
            cur.execute("SELECT developer_id FROM developers ORDER BY developer_id DESC LIMIT 1")
            lastDevId = cur.fetchall()[0][0]
            lastDevDigit = int(lastDevId.split('-')[1]) + 1
            if(lastDevDigit < 10):
                newDevId = lastDevId.split('-')[0] + '-0'+str(lastDevDigit)
            else:
                newDevId = lastDevId.split('-')[0] +str(lastDevDigit)
            cur.execute("INSERT INTO developers (developer_id, lastname, firstname, phone, address, city, state, country, active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (f"{newDevId}", f"{data['lastname']}", data['firstname'], f"{data['phone']}",
                         f"{data['address']}", f"{data['city']}", f"{data['state']}", f"{data['country']}", "TRUE"))
            con.commit()
            return '200'    

    @app.route('/developers/delete')
    def delete_developer():
            developerId = request.args.get('developerId')
            cur.execute(f'UPDATE developers SET active = FALSE WHERE developer_id = \'{developerId}\'')
            cur.execute(f'UPDATE developer_asset SET to_date = CURRENT_DATE WHERE developer_asset.developer_id = \'{developerId}\'')
            return '200'    

    @app.route('/licenses/')
    def fetch_licenses_by_developerId():
            developerId = request.args.get('developerId')
            cur.execute(f'SELECT * FROM developer_license WHERE developer_id = \'{developerId}\'')
            rows = cur.fetchall()
            print(rows)
            return jsonify(rows)
   
    @app.route('/assets/history')
    def fetch_asset_history():
            assetId = request.args.get('assetId')
            cur.execute(f'SELECT * FROM developers d INNER JOIN developer_asset d_a ON d.developer_id = d_a.developer_id INNER JOIN assets a ON a.asset_id = d_a.asset_id WHERE a.asset_id = \'{assetId}\'')
            rows = cur.fetchall()
            print(rows)
            return jsonify(rows)

    @app.route('/overview/availableAssets')
    def fetch_all_available_assets():
            cur.execute(f'SELECT * from assets a full outer join developer_asset d_a on a.asset_id = d_a.asset_id WHERE d_a.to_date IS NOT NULL OR d_a.developer_id IS NULL')
            rows = cur.fetchall()
            print(rows)
            return jsonify(rows)

    @app.route('/overview/addRegister', methods=['GET', 'POST'])
    def add_register():
        if request.method == 'POST':
            data = request.form.to_dict()
            print('data: ', data, file=sys.stderr)
            cur.execute("INSERT INTO developer_asset (developer_id, asset_id, from_date) VALUES (%s, %s, current_timestamp)",
                        (f"{data['developerId']}", data['assetId']))
            con.commit()
            return '200'        

    @app.route('/overview')
    def fetch_all_assigned_assets():
            cur.execute(f'SELECT * from assets a full outer join developer_asset d_a inner join developers d on d_a.developer_id = d.developer_id on a.asset_id = d_a.asset_id WHERE d_a.from_date IS NOT NULL AND d_a.to_date IS NULL')
            rows = cur.fetchall()
            print(rows)
            return jsonify(rows)


except:
    print('Error')