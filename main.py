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
        
        # Video dosyası bul
        video_files = ["data/videos/1.mp4", "data/videos/2.mp4", "data/videos/3.mp4", "data/videos/4.mp4"]
        
        for video in video_files:
            if Path(video).exists():
                print(f"Video: {video}")
                detector.run_video(video)
                break
        else:
            print("Video dosyası bulunamadı!")
            
    except Exception as e:
        print(f"Hata: {e}")

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
