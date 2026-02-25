import threading
from crawler import crawl


def start_crawl():

    update_button.config(state="disabled")
    progress_bar["value"] = 0

    def thread_target():
        crawl(
            progress_callback=lambda p: root.after(0, update_progress, p),
            status_callback=lambda s: root.after(0, update_status, s)
        )
        root.after(0, crawl_finished)

    threading.Thread(target=thread_target, daemon=True).start()


def update_progress(value):
    progress_bar["value"] = value


def update_status(text):
    status_label.config(text=text)


def crawl_finished():
    update_button.config(state="normal")
    status_label.config(text="Update Complete")
