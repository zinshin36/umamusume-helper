def update_database(self):

    try:
        api = UmaAPI(progress_callback=self.update_progress)

        horses = api.fetch_all_horses()
        supports = api.fetch_all_supports()

        self.data_manager.save(horses, supports)

        self.horses = horses
        self.supports = supports

        self.root.after(0, self.update_complete)

    except Exception as e:

        def fail():
            self.status_label.config(text="API Error")
            self.update_btn.config(state="normal")
            messagebox.showerror("API Error", str(e))

        self.root.after(0, fail)
