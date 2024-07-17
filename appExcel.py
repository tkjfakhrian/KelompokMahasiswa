import streamlit as st
from streamlit_option_menu import option_menu
import streamlit as st
import pandas as pd
import numpy as np
import math

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from functools import reduce
from pprint import pprint
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as sch
from io import BytesIO

class MainClass() :
    def __init__(self):
        self.data = Data()
        self.kelompok = Kelompok()
        self.representasi = Representasi()

    # Fungsi judul halaman
    def judul_halaman(self):
        nama_app = "Prototype Aplikasi Prediksi Kelulusan Mahasiswa"
        st.title(nama_app)

    # Fungsi menu sidebar
    def sidebar_menu(self):
        with st.sidebar:
            selected = option_menu('Menu',['Upload Data','Kelompok Mahasiswa','Representasi Kelompok'],
            icons =["easel2", "table","paperclip"],
            menu_icon="cast",
            default_index=0)
            
        if (selected == 'Upload Data'):
            self.data.menu_data()

        if (selected == 'Kelompok Mahasiswa'):
            self.kelompok.kelompok_mhs()

        if (selected == 'Representasi Kelompok') :
            self.representasi.kelompok_mhs()

class Data(MainClass) :
    def __init__(self):
        self.state = st.session_state.setdefault('state', {})
        if 'DataMahasiswa' not in self.state:
            self.state['DataMahasiswa'] = pd.DataFrame()

    def upload_DataMahasiswa(self):
        try:
            uploaded_file = st.file_uploader("Upload Data Mahasiswa", type=["xlsx"], key="DataMahasiswa")
            if uploaded_file is not None:
                self.state['DataMahasiswa'] = pd.DataFrame()
                DataMahasiswa = pd.read_excel(uploaded_file)

                self.state['DataMahasiswa'] = DataMahasiswa
        except(KeyError, IndexError):
            st.error("Data yang diupload tidak sesuai")

    def tampil_DataMahasiswa(self) :
        if not self.state['DataMahasiswa'].empty:
            Data = self.state['DataMahasiswa']
            Data['NIM'] = Data['NIM'].astype(str)
            st.dataframe(Data)

    def menu_data(self):
        self.judul_halaman()
        self.upload_DataMahasiswa()
        self.tampil_DataMahasiswa()
        
class Kelompok(Data) :
    def __init__(self) :
        self.state = st.session_state.setdefault('state', {})
        if 'DataMahasiswa' not in self.state :
            self.state['DataMahasiswa'] = pd.DataFrame()

        if 'Jml_Cluster' not in self.state :
            self.state['Jml_Cluster'] = 0

        if 'smallest_x' not in self.state :
            self.state['smallest_x'] = '-'
            self.state['second_smallest_x'] = '-'
        
    def representasi_kelompok(self,df,kelompok) :
        anggota_kelas = df[df['cluster'] == kelompok + 1]

        #Karakteristik Dari Anggota Kelas
        st.write(f"- Kelompok : **{kelompok+1}**, Memiliki Anggota Sebanyak : **{len(anggota_kelas)}**")

        #Expander Karakteristik
        with st.expander(f"Karakteristik Kelompok : **{kelompok+1}**") :
            st.write('Anggota Kelompok')
            st.dataframe(anggota_kelas[['NIM','NAMA']])
            
            st.write('Karakteristik Sekolah')
            sekolah = anggota_kelas['Tipe_Sekolah'].value_counts()
            st.dataframe(sekolah.head(3))

            st.write('Karakteristik Semester')
            semester = anggota_kelas['Jml_SMS_Saat_Ini'].value_counts()
            st.dataframe(semester.head())

            #Rata-rata IPK
            rata_ipk = anggota_kelas['IPK'].mean()
            st.write(f'Rata-rata IPK : {rata_ipk:2.2f}')

            st.write('Karakteristik Cuti')
            cuti = anggota_kelas['Jml_Cuti'].value_counts()
            st.dataframe(cuti.head())

    def KMeans(self,DataMahasiswa,Jml_Cluster) :
        data_encoded = pd.get_dummies(DataMahasiswa[['IPK', 'SKS', 'Jml_SMS_Saat_Ini', 'Jml_Cuti', 'Tipe_Sekolah']])
        
        #Standarisasi Data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data_encoded)

        #Inisialisasi Model K-Means
        kmeans = KMeans(n_clusters=Jml_Cluster,random_state=42)
                    
        #Membuat Model K-Means
        kmeans.fit(scaled_data)

        #Mendapatkan label cluster
        labels = kmeans.labels_ + 1

        #Menambahkan label cluster ke dataframe asli
        DataMahasiswa['cluster'] = labels

        #Encode
        DataMahasiswa['Tipe_Sekolah'] = DataMahasiswa['Tipe_Sekolah'].replace([1,2,3],['Lainnya (MA/Pesantren/homeshooling)','SMK','SMA Umum/PGRI/Plus'])

    def kelompok_mhs(self) :
        self.judul_halaman()
        try :
            DataMahasiswa = self.state['DataMahasiswa']
            #data_encoded = pd.get_dummies(DataMahasiswa[['IPK', 'SKS', 'Jml_SMS_Saat_Ini', 'Jml_Cuti', 'Tipe_Sekolah']]) 

            if self.state['Jml_Cluster'] <= 0 :
                Jml_Cluster = int(st.number_input('Masukkan Jumlah Kelompok Yang Akan Dibentuk : '))
                self.state['Jml_Cluster'] = Jml_Cluster
                if st.button('Bentuk Kelompok') and self.state['Jml_Cluster'] > 0:
                    self.KMeans(DataMahasiswa,self.state['Jml_Cluster'])
                    self.state['Representasi'] = False
                else :
                    st.write('Mohon Masukkan Jumlah Kelompok Terlebih Dahulu')
            else :
                st.write(f"Jumlah Kelompok Yang Dipilih : **{self.state['Jml_Cluster']}**")
                self.KMeans(DataMahasiswa,self.state['Jml_Cluster'])
                self.state['Representasi'] = False

            #Representasi Pengetahuan
            for i in range(self.state['Jml_Cluster']) :
                self.representasi_kelompok(DataMahasiswa,i)           
            
        except :
            st.write('Upload File Terlebih Dahulu')         

class Representasi(Data) :
    def __init__(self) :
        self.state = st.session_state.setdefault('state', {})
        if 'DataMahasiswa' not in self.state:
            self.state['DataMahasiswa'] = pd.DataFrame()
        
        if 'Representasi' not in self.state :
            self.state['Representasi'] = False

    def to_excel(self,df) :
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Kelompok Mahasiswa')
        writer.close()
        processed_data = output.getvalue()
        return processed_data

    def representasi_kelompok(self,df,kelompok) :
        anggota_kelas = df[df['cluster'] == kelompok]

        #Karakteristik Dari Anggota Kelas
        st.write(f"- Kelompok : **{kelompok}**, Memiliki Anggota Sebanyak : **{len(anggota_kelas)}**")

        #Expander Karakteristik
        with st.expander(f"Karakteristik Kelompok : **{kelompok}**") :
            #Rata-rata IPK
            rata_ipk = anggota_kelas['IPK'].mean()
            rata_SKS = anggota_kelas['SKS'].mean()
            st.write(f'Anggota memiliki rata-rata IPK : **{rata_ipk:2.2f}** dengan rata-rata SKS yang sudah diselesaikan **{rata_SKS:2.0f}**')

    def kelompok_mhs(self) :
        self.judul_halaman()
        try :
            DataMahasiswa = self.state['DataMahasiswa']
            if self.state['Representasi'] == False :
                #Get Label Cluster
                unique_clusters = DataMahasiswa['cluster'].unique()

                #Dictionary Untuk Label Cluster Baru
                new_labels = {}
                
                #Loop unique cluster
                for cluster in unique_clusters :
                    label_kelompok = st.text_input(f'Masukkan Label Kelompok {cluster}', key=f'label_{cluster}')
                    new_labels[cluster] = label_kelompok

                #Button untuk update DataFrame
                if st.button('Represent Kelompok') :
                    for cluster,label_kelompok in new_labels.items():
                        if label_kelompok :
                            DataMahasiswa['cluster'] = DataMahasiswa['cluster'].replace(cluster,label_kelompok)
                
                    self.state['Representasi'] = True
                    self.kelompok_mhs()
            else :
                st.header('Proporsi Kelompok')
                #Pie Chart Proporsi
                cluster_counts = DataMahasiswa['cluster'].value_counts()

                #Pie Chart
                fig, ax = plt.subplots()
                ax.pie(cluster_counts, labels=cluster_counts.index, autopct='%.2f %%', startangle=90)
                ax.axis('equal') #Equal aspect ratio
                st.pyplot(fig)

                st.dataframe(DataMahasiswa)

                #Download Ke Excel
                excel_data = self.to_excel(DataMahasiswa)
                st.download_button(label='Unduh Hasil Cluster', data=excel_data, file_name='Hasil_Clustering_Mahasiswa.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

                #Get Label Cluster
                unique_clusters = DataMahasiswa['cluster'].unique()

                for cluster in unique_clusters :
                    self.representasi_kelompok(DataMahasiswa,cluster) 
        except :
            st.write('Upload File Terlebih Dahulu')

if __name__ == "__main__":
    # Create an instance of the main class
    main = MainClass()
    
main.sidebar_menu()
