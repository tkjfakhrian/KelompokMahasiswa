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

    # Fungsi judul halaman
    def judul_halaman(self):
        nama_app = "Prototype Aplikasi Penentuan Kelulusan Mahasiswa"
        st.title(nama_app)

    # Fungsi menu sidebar
    def sidebar_menu(self):
        with st.sidebar:
            selected = option_menu('Menu',['Upload Data','Kelompok Mahasiswa'],
            icons =["easel2", "table"],
            menu_icon="cast",
            default_index=0)
            
        if (selected == 'Upload Data'):
            self.data.menu_data()

        if (selected == 'Kelompok Mahasiswa'):
            self.kelompok.kelompok_mhs()

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
            st.dataframe(Data)

    def menu_data(self):
        self.judul_halaman()
        self.upload_DataMahasiswa()
        self.tampil_DataMahasiswa()

class DBI(Data) :
    def __init__(self) :
        self.state = st.session_state.setdefault('state', {})
        if 'DataPenerimaan' not in self.state:
            self.state['DataPenerimaan'] = pd.DataFrame()

    def RekomendasiDBI(self) :
        self.judul_halaman()
        #try :
            #DataPenerimaan = self.state['DataPenerimaan'] 
            #results = {}
            #for i in range(2,8) :
                #hc = AgglomerativeClustering(n_clusters=i, affinity='euclidean',linkage='ward')
                #y_hc = hc.fit_predict(DataPenerimaan)
                #db_index = davies_bouldin_score(DataPenerimaan,y_hc)
                #results.update({i:db_index})

            #convert dictionary to DataFrame
            #df = pd.DataFrame(list(results.items()), columns=['Jml_Clusters','Nilai_DBI'])

            #convert 'X' to numeric
            #df['Jml_Clusters'] = pd.to_numeric(df['Jml_Clusters'])

            #Display the DataFrame
            #st.markdown(
            #    """
            #    <style>
            #    .dataframe tbody tr th, .dataframe tbody tr td {
            #        text-align: center;
            #    }
            #    </style>
            #    """,
            #    unsafe_allow_html=True
            #)
            #st.table(df)

            #Mencari Nilai Terkecil
            #smallest_value = df['Nilai_DBI'].min()
            #second_smallest_value = df['Nilai_DBI'].nsmallest(2).iloc[-1]

            #Mencari corresponding 'Jml_Clusters' values
            #smallest_x = df[df['Nilai_DBI'] == smallest_value]['Jml_Clusters'].values[0]
            #second_smallest_x = df[df['Nilai_DBI'] == second_smallest_value]['Jml_Clusters'].values[0]

            #self.state['smallest_x'] = smallest_x
            #self.state['second_smallest_x'] = second_smallest_x

            #Create Line Plot
            #fig,ax = plt.subplots()
            #ax.plot(df['Jml_Clusters'], df['Nilai_DBI'], marker='o')
            #ax.set_xlabel('Jumlah Clusters')
            #ax.set_ylabel('Nilai Davies-Boulding Index')
            #ax.set_title('Grafik Rekomendasi DBI')

            #Highlight nilai terkecil dan nilai terkecil kedua
            #ax.plot(smallest_x,smallest_value,marker='o',markersize=10,color='red',label='Jml Cluster Terbaik Ke-1')
            #ax.plot(second_smallest_x,second_smallest_value,marker='o',markersize=10,color='orange',label='Jml Cluster Terbaik Ke-2')
            #ax.legend()

            #display plot
            #st.pyplot(fig)

            #Kesimpulan
            #st.write("### Kesimpulan :")
            #st.write(f"- Rekomendasi Kelompok Ke-1 Memiliki Nilai DBI : **{smallest_value:.5f}**, Sehingga Konten Promosi Dapat Dibuat Sebanyak : **{smallest_x}** Konten Promosi")
            #st.write(f"- Rekomendasi Kelompok Ke-2 Memiliki Nilai DBI : **{second_smallest_value:.5f}** Sehingga Konten Promosi Dapat Dibuat Sebanyak : **{second_smallest_x}** Konten Promosi")


        #except :
            #st.write('Upload File Terlebih Dahulu')

class Kelompok(Data) :
    def __init__(self) :
        self.state = st.session_state.setdefault('state', {})
        if 'DataPenerimaan' not in self.state:
            self.state['DataPenerimaan'] = pd.DataFrame()

        if 'smallest_x' not in self.state :
            self.state['smallest_x'] = '-'
            self.state['second_smallest_x'] = '-'
        
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

    def kelompok_mhs(self) :
        self.judul_halaman()
        try :
            DataMahasiswa = self.state['DataMahasiswa']
            data_encoded = pd.get_dummies(DataMahasiswa[['IPK', 'SKS', 'Jml_SMS_Saat_Ini', 'Jml_Cuti', 'Tipe_Sekolah']]) 

            jml_cluster = int(st.number_input('Masukkan Jumlah Kelompok Yang Akan Dibentuk : '))
            if st.button('Simulasikan') and jml_cluster > 0:
                
                #Standarisasi Data
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(data_encoded)

                #Inisialisasi Model K-Means
                kmeans = KMeans(n_clusters=jml_cluster,random_state=42)
                
                #Membuat Model K-Means
                kmeans.fit(scaled_data)

                #Mendapatkan label cluster
                labels = kmeans.labels_

                #Menambahkan label cluster ke dataframe asli
                DataMahasiswa['cluster'] = labels

                #Encode
                DataMahasiswa['Tipe_Sekolah'] = DataMahasiswa['Tipe_Sekolah'].replace([1,2,3],['Lainnya (MA/Pesantren/homeshooling)','SMK','SMA Umum/PGRI/Plus'])

                st.dataframe(DataMahasiswa)
                #Download Ke Excel
                excel_data = self.to_excel(DataMahasiswa)
                st.download_button(label='Unduh Excel', data=excel_data, file_name='Hasil_Clustering_Mahasiswa.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

                #Representasi Pengetahuan
                for i in range(jml_cluster) :
                    self.representasi_kelompok(DataMahasiswa,i)

            else :
                st.write('Mohon Masukkan Jumlah Simulasi Terlebih Dahulu')

        except :
            st.write('Upload File Terlebih Dahulu')         

if __name__ == "__main__":
    # Create an instance of the main class
    main = MainClass()
    
main.sidebar_menu()