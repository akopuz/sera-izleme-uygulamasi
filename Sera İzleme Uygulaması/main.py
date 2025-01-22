import subprocess
import time

def start_application(app_path):
    try:
        subprocess.Popen(['python', app_path])
        print(f"{app_path} başarıyla başlatıldı.")
    except Exception as e:
        print(f"Uygulama başlatılamadı: {e}")

def main():
    apps = ['frontend_server.py', 'sensor_database_adapter.py', 'rules_adapter.py', 'real_time_data.py', 'notification_sender.py', 'query_service.py']

    for app in apps:
        print(f"{app} başlatılıyor...")
        start_application(app)
        time.sleep(2)  

    print("Tüm uygulamalar başlatıldı.")

if __name__ == "__main__":
    main()