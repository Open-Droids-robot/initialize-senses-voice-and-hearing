#!/usr/bin/env python3
"""
Test script to check if keyboard input detection is working.
"""

import sys
import time
import threading

def test_input_detection():
    """Test basic input detection."""
    print("Testing input detection...")
    print("Press SPACE to pause, 'q' to quit, or any other key to test")
    print("=" * 50)
    
    def input_loop():
        while True:
            try:
                # Try select-based input detection
                import select
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    if key == ' ':
                        print("✅ SPACE detected!")
                    elif key == 'q':
                        print("✅ 'q' detected! Exiting...")
                        break
                    else:
                        print(f"✅ Key '{key}' detected!")
                        
            except ImportError:
                # Try Windows-style input detection
                try:
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8')
                        if key == ' ':
                            print("✅ SPACE detected!")
                        elif key == 'q':
                            print("✅ 'q' detected! Exiting...")
                            break
                        else:
                            print(f"✅ Key '{key}' detected!")
                except:
                    print("❌ No input detection method available")
                    break
            except Exception as e:
                print(f"❌ Input detection error: {e}")
                break
    
    # Run input detection in a separate thread
    input_thread = threading.Thread(target=input_loop, daemon=True)
    input_thread.start()
    
    # Main loop with status updates
    try:
        count = 0
        while input_thread.is_alive():
            print(f"Waiting for input... ({count})", end='\r')
            count += 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    print("\nInput test completed!")

if __name__ == "__main__":
    test_input_detection()
