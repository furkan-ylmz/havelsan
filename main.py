#!/usr/bin/env python3
"""
AIS-Kamera Eşleştirme Sistemi - Ana Script
"""

import sys
from pathlib import Path

def show_menu():
    print("🚢 AIS-Kamera Eşleştirme Sistemi")
    print("=" * 40)
    print("1. Test verilerini analiz et")
    print("2. Video testi yap")
    print("3. Çıkış")
    print()

def run_analysis():
    print("Test analizi başlatılıyor...")
    try:
        from ais_matcher import process_test_data
        process_test_data()
    except Exception as e:
        print(f"Hata: {e}")

def run_video_test():
    print("Video testi başlatılıyor...")
    try:
        from simple_detector import SimpleDetector
        detector = SimpleDetector()
        
        # Mevcut video dosyalarını bul
        video_files = []
        for i in range(1, 5):  # 1.mp4, 2.mp4, 3.mp4, 4.mp4
            video_path = f"data/videos/{i}.mp4"
            if Path(video_path).exists():
                video_files.append(video_path)
        
        if not video_files:
            print("❌ Video dosyası bulunamadı!")
            return
            
        # Video seçimi menüsü
        print("\nMevcut videolar:")
        for i, video in enumerate(video_files):
            print(f"{i+1}. {video}")
        print(f"{len(video_files)+1}. Tümünü çalıştır")
        
        choice = input(f"\nSeçiminiz (1-{len(video_files)+1}): ").strip()
        
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(video_files):
                # Tek video çalıştır
                selected_video = video_files[choice_num - 1]
                print(f"\n🎥 Video çalıştırılıyor: {selected_video}")
                detector.run_video(selected_video)
            elif choice_num == len(video_files) + 1:
                # Tüm videoları sırayla çalıştır
                for video in video_files:
                    print(f"\n🎥 Video çalıştırılıyor: {video}")
                    detector.run_video(video)
                    input("Sonraki video için Enter'a basın...")
            else:
                print("❌ Geçersiz seçim!")
        else:
            print("❌ Geçersiz seçim!")
            
    except Exception as e:
        print(f"❌ Hata: {e}")

def main():
    while True:
        show_menu()
        
        try:
            choice = input("Seçiminiz (1-3): ").strip()
            
            if choice == '1':
                run_analysis()
            elif choice == '2':
                run_video_test()
            elif choice == '3':
                print("Çıkış yapılıyor...")
                break
            else:
                print("Geçersiz seçim!")
                
        except (KeyboardInterrupt, EOFError):
            print("\nÇıkış yapılıyor...")
            break
            
        input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    main()
