import traceback
import cv2
from aiTrainer import aiTrainer
from guiModule import shotGUI
import threading
import queue
import time



def main():
    
    gui = shotGUI()
    trainer = aiTrainer(cam_index= 0)
    
    # Set up ROI (region of interest) for hoop detection
    trainer.setupROI()
    
    # DEBUG: camera state if available
    if hasattr(trainer, "cap"):
        try:
            print("DEBUG: trainer.cap.isOpened():", trainer.cap.isOpened())
        except Exception as e:
            print("DEBUG: checking trainer.cap failed:", e)
    else:
        print("DEBUG: trainer has no .cap attribute")

    running = True

    # small queue to transfer frames from worker -> main thread (GUI)
    frame_q = queue.Queue(maxsize=2)
    frame_count = 0

    def updateLoop():
        nonlocal running, frame_count
        try:
            while running:
                frame, stats = trainer.processFrame()
                frame_count += 1
                if frame is not None:
                    # convert BGR to RGB here (worker) and push to queue
                    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    try:
                        frame_q.put_nowait((frameRGB, stats))
                        print(f"DEBUG: queued frame #{frame_count}")
                    except queue.Full:
                        # drop frame if GUI is lagging
                        print(f"DEBUG: dropped frame #{frame_count} (queue full)")
                        pass
                else:
                    print(f"DEBUG: processFrame returned None on iteration #{frame_count}")
                # yield a bit to avoid busy loop and limit CPU usage
                time.sleep(0.01)
        except Exception:
            traceback.print_exc()
            running = False

    thread = threading.Thread(target=updateLoop, daemon=True)
    thread.start()
    print("DEBUG: update thread started")

    # Poll queue from main (Tk) thread and update GUI there
    def pollQueue():
        nonlocal running
        try:
            processed = 0
            while not frame_q.empty():
                frameRGB, stats = frame_q.get_nowait()
                processed += 1
                try:
                    gui.updateVideo(frameRGB)
                    if stats:
                        gui.updateStats(stats)
                    print(f"DEBUG: pollQueue updated GUI with {processed} frames")
                except Exception:
                    # GUI update error (still on main thread) — print and continue
                    traceback.print_exc()
                    
        except Exception:
            traceback.print_exc()
        # schedule next poll if GUI exposes a Tk root
        if running:
            root = getattr(gui, "root", None)
            if root is not None:
                root.after(30, pollQueue)

    # start polling before entering GUI mainloop
    root = getattr(gui, "root", None)

    if root is not None:
        print("DEBUG: scheduling pollQueue via root.after")
        root.after(0, pollQueue)
    else:
        print(" shotGUI has no .root ")



    try:
        gui.run()
    except Exception:
        traceback.print_exc()
    finally:
        running = False
        thread.join(timeout=1.0)
        trainer.release()

if __name__ == "__main__":
    main()