import os
import shutil
import subprocess
import sys
from tkinter import *
from tkinter import filedialog, messagebox, simpledialog

# Konfigurasi
MAIN_DIR = "video"  # Direktori utama
SUPPORTED_FORMATS = [  # Format file yang didukung
    ('Video Files', '*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.mpeg *.mpg *.m4v *.webm'),
    ('All Files', '*.*')
]

def get_vlc_path():
    """Mencari lokasi VLC secara otomatis di berbagai platform"""
    if sys.platform.startswith('win'):
        default_paths = [
            "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
            "C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe"
        ]
    elif sys.platform.startswith('darwin'):
        default_paths = ["/Applications/VLC.app/Contents/MacOS/VLC"]
    else:
        default_paths = ["/usr/bin/vlc", "/usr/local/bin/vlc", "/snap/bin/vlc"]

    for path in default_paths:
        if os.path.isfile(path):
            return path
    return filedialog.askopenfilename(title="Temukan VLC Player", filetypes=[("Executable", "*.exe")])

class Video_Photo_Sorter:
    def __init__(self, root):
        self.root = root
        self.root.title("Video And Photo Sorter Pro")
        self.root.geometry("800x500")
        self.root.resizable(True, True)
        
        # Cek dan buat direktori utama jika belum ada
        if not os.path.exists(MAIN_DIR):
            os.makedirs(MAIN_DIR)
        
        # Inisialisasi path saat ini
        self.current_dir = MAIN_DIR
        
        # Style
        self.button_style = {'padx': 10, 'pady': 5, 'bd': 2}
        self.listbox_font = ('Arial', 10)
        
        # UI Elements
        self.create_widgets()
        self.update_listbox()
        self.create_folder_buttons()
        
        # VLC Path
        self.vlc_path = get_vlc_path()
        if not self.vlc_path:
            messagebox.showerror("Error", "VLC Player tidak ditemukan!")
            self.root.destroy()

    def create_widgets(self):
        # Frame utama
        main_frame = Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Label path saat ini
        self.path_label = Label(main_frame, text=f"Path: {self.current_dir}", font=("Arial", 10), anchor=W)
        self.path_label.pack(fill=X, pady=5)

        # Listbox dengan scrollbar
        list_frame = Frame(main_frame)
        list_frame.pack(fill=BOTH, expand=True)
        
        self.listbox = Listbox(
            list_frame, 
            selectmode=SINGLE, 
            font=self.listbox_font,
            activestyle='dotbox'
        )
        scrollbar = Scrollbar(list_frame, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.pack(fill=BOTH, expand=True)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        # Tombol aksi
        btn_frame = Frame(main_frame)
        btn_frame.pack(fill=X, pady=5)
        
        Button(btn_frame, text="Tambah Video", command=self.add_video, **self.button_style).pack(side=LEFT)
        Button(btn_frame, text="Putar", command=self.play_video, **self.button_style).pack(side=LEFT)
        Button(btn_frame, text="Rename", command=self.rename_file, **self.button_style).pack(side=LEFT)
        Button(btn_frame, text="Hapus", command=self.delete_file, **self.button_style).pack(side=LEFT)
        Button(btn_frame, text="Pindahkan ke Folder...", command=self.move_to_folder, **self.button_style).pack(side=LEFT)
        Button(btn_frame, text="Buat Folder Baru", command=self.create_folder, **self.button_style).pack(side=RIGHT)
        Button(btn_frame, text="Refresh", command=self.refresh_all, **self.button_style).pack(side=RIGHT)

        # Folder buttons frame
        self.folder_frame = Frame(main_frame)
        self.folder_frame.pack(fill=X, pady=5)

        # Tombol navigasi
        Button(main_frame, text="Kembali ke Folder Utama", command=self.go_to_main_dir, **self.button_style).pack(pady=5)

    def go_to_main_dir(self):
        """Kembali ke folder utama"""
        self.current_dir = MAIN_DIR
        self.update_listbox()
        self.create_folder_buttons()
        self.path_label.config(text=f"Path: {self.current_dir}")

    def refresh_all(self):
        self.update_listbox()
        self.create_folder_buttons()

    def get_selected_file(self):
        try:
            selection = self.listbox.get(self.listbox.curselection()[0])
            if "[Folder]" in selection:
                return None
            return selection
        except IndexError:
            messagebox.showwarning("Peringatan", "Silakan pilih file terlebih dahulu!")
            return None

    def add_video(self):
        files = filedialog.askopenfilenames(
            initialdir=MAIN_DIR,
            title="Pilih Video",
            filetypes=SUPPORTED_FORMATS
        )
        for file in files:
            try:
                shutil.copy(file, self.current_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menambahkan file:\n{str(e)}")
        self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, END)
        items = os.listdir(self.current_dir)
        
        # Pisahkan folder dan file
        folders = [f for f in items if os.path.isdir(os.path.join(self.current_dir, f))]
        files = [f for f in items if os.path.isfile(os.path.join(self.current_dir, f))]
        
        # Tampilkan folder terlebih dahulu
        for folder in sorted(folders):
            self.listbox.insert(END, f"[Folder] {folder}")
        
        # Tampilkan file
        for f in sorted(files):
            self.listbox.insert(END, f)

    def play_video(self):
        if (file := self.get_selected_file()):
            try:
                subprocess.Popen([self.vlc_path, os.path.join(self.current_dir, file)])
            except Exception as e:
                messagebox.showerror("Error", f"Gagal memutar video:\n{str(e)}")

    def move_to_folder(self):
        """Memindahkan file ke folder yang dipilih"""
        if (file := self.get_selected_file()):
            # Dapatkan daftar folder yang tersedia
            folders = [f for f in os.listdir(self.current_dir) if os.path.isdir(os.path.join(self.current_dir, f))]
            
            if not folders:
                messagebox.showwarning("Peringatan", "Tidak ada folder yang tersedia!")
                return
            
            # Buat dialog untuk memilih folder
            folder = simpledialog.askstring(
                "Pindahkan ke Folder",
                "Masukkan nama folder tujuan:",
                initialvalue=folders[0] if folders else ""
            )
            
            if folder and folder in folders:
                source = os.path.join(self.current_dir, file)
                destination = os.path.join(self.current_dir, folder, file)
                try:
                    shutil.move(source, destination)
                    self.update_listbox()
                    messagebox.showinfo("Berhasil", f"File berhasil dipindahkan ke {folder}")
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal memindahkan file:\n{str(e)}")
            else:
                messagebox.showwarning("Peringatan", "Folder tidak valid!")

    def rename_file(self):
        if (file := self.get_selected_file()):
            new_name = simpledialog.askstring("Rename", "Nama baru:", initialvalue=file)
            if new_name and new_name != file:
                try:
                    os.rename(
                        os.path.join(self.current_dir, file),
                        os.path.join(self.current_dir, new_name)
                    )
                    self.update_listbox()
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal mengubah nama:\n{str(e)}")

    def delete_file(self):
        if (file := self.get_selected_file()):
            if messagebox.askyesno("Konfirmasi", f"Hapus {file} secara permanen?"):
                try:
                    os.remove(os.path.join(self.current_dir, file))
                    self.update_listbox()
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal menghapus file:\n{str(e)}")

    def create_folder(self):
        name = simpledialog.askstring("Folder Baru", "Nama folder:")
        if name:
            try:
                os.makedirs(os.path.join(self.current_dir, name), exist_ok=True)
                self.create_folder_buttons()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membuat folder:\n{str(e)}")

    def create_folder_buttons(self):
        # Hapus tombol lama
        for widget in self.folder_frame.winfo_children():
            widget.destroy()

        # Buat tombol baru
        folders = [f for f in os.listdir(self.current_dir) 
                  if os.path.isdir(os.path.join(self.current_dir, f)) and not f.startswith('.')]
        
        for folder in sorted(folders):
            Button(
                self.folder_frame,
                text=f"Masuk ke {folder}",
                command=lambda f=folder: self.enter_folder(f),
                **self.button_style
            ).pack(side=LEFT, padx=2)

    def enter_folder(self, folder):
        """Masuk ke folder yang dipilih"""
        self.current_dir = os.path.join(self.current_dir, folder)
        self.update_listbox()
        self.create_folder_buttons()
        self.path_label.config(text=f"Path: {self.current_dir}")

if __name__ == "__main__":
    root = Tk()
    app = Video_Photo_Sorter(root)  # Buat instance aplikasi
    root.mainloop()