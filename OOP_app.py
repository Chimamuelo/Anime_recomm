from os.path import basename
import requests
from tkinter import *
from tkinter.ttk import *
from numpy.lib.arraypad import pad
import pandas as pd
import matplotlib.pyplot as plt
from tkinter.filedialog import askopenfilename
from bs4 import BeautifulSoup
from PIL import ImageTk,Image
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Application(Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.master=master
        self.create_widgets()
      
    def create_widgets(self):

        self.menu=Menu(self.master)
        self.master.config(menu=self.menu)

        self.file_menu=Menu(self.menu,tearoff=False)
        self.menu.add_cascade(label='File',menu=self.file_menu)
        self.file_menu.add_command(label='Open',command=self.open_file)
        
        #Reference frame
        self.frame1=Frame(self.master)
        self.frame2=Frame(self.master)
        self.frame3=Frame(self.master)

        self.style=Style()
        self.style.theme_use('classic')

        #File label
        self.file_label=Label(self.master,text='')

        #textlabel
        self.txtlabel=Text(self.master,height=10,font=('Times New Roman',14))
        self.synopsis=Label(self.master,text='Synopsis',font=('Arial',25))

        #tree structure(simulate pandas df)
        self.tree=Treeview(self.frame1)
        #bind this to left click
        self.tree.bind("<Button-3>",self.left_click)
        self.tree2=Treeview(self.master)
        #self.tree2.bind("<Button-3>",self.left_click)

        
        #ADD a scrollingbar in y axis(attached to the anime df)
        self.scrollbarY = Scrollbar(self.frame1, orient=VERTICAL, command=self.tree.yview)
        self.scrollbarY.pack(pady=10,side=RIGHT,fill='y')
        self.tree.configure(yscroll=self.scrollbarY.set)

        #Search bar( search animes,include sub word)
        self.search= Entry(self.frame2,width=40)
        self.search.pack(pady=10,side=RIGHT)
        #bind this search bar by the key enter(return) to perform command get name
        self.search.bind('<Return>',self.get_name)

        self.search_label=Label(self.frame2,text='Search Anime')
        self.search_label.pack(pady=10,side=LEFT)

        #Add sub menu (left click) to allow certain commands
        self.submenu=Menu(self.tree,tearoff=0)
        self.submenu.add_command(label ="Select anime",command=self.show_info)
        self.submenu.add_command(label ="Delete",command=self.delete_item)

        #Image canvas
        self.canvas = Canvas(self.frame3,height=300,width=300)
        self.canvas.pack()

        #Button command for recomendations 
        self.my_button=Button(self.frame3,text='Recommendation',style='D.TButton',command=self.recommend_similar)
        self.my_button.pack(side=RIGHT)



#open file
    def open_file(self):
        global df
        filename=askopenfilename(title='Open File',filetypes=[("Excel File", ".xlsx .xls"),("Csv File", ".csv")])
                           
        #handle errors (file does not exist)
        if filename:
            try:
                filename=r"{}".format(filename)
                df=pd.read_csv(filename)
                self.frame1.pack(fill='x')
                self.frame2.pack()
            except ValueError:
                self.file_label.config(text='File error')
                self.file_label.pack()
            except FileExistsError:
                self.file_label.config(text='NO')
                self.file_label.pack(pady=20)


        self.clear_tree()
        #Getting information about df
        #df['name']=df['name'].str.replace(':','')
        self.tree['column']=list(df.columns)
        self.tree['show']='headings'
        for column in self.tree['column']:
            self.tree.heading(column,text=column)
    
        df_rows=df.to_numpy().tolist()

        for row in df_rows:
            self.tree.insert('','end',values=row)
    
        self.tree.pack(pady=20,fill='x')

    def clear_tree(self):
        self.tree.delete(*self.tree.get_children())
    def clear_tree2(self):
        self.tree2.delete(*self.tree2.get_children())

    def get_name(self,placeholder):
        self.clear_tree()
        subword=self.search.get()
   
        if  not subword.strip():
            df2=df
            self.tree['column']=list(df2.columns)
            self.tree['show']='headings'
            for column in self.tree['column']:
                self.tree.heading(column,text=column)
            rows=df2.to_numpy().tolist()
            for row in rows:
                self.tree.insert('','end',values=row)

        else:

            df2 = df[df['name'].str.contains(subword, na=False, case=False)]
            df2=df2.sort_values('members',ascending=False)
            sub_df=df2.head(10)
            self.tree['column']=list(sub_df.columns)
            self.tree['show']='headings'
            for column in self.tree['column']:
                self.tree.heading(column,text=column)
            rows=sub_df.to_numpy().tolist()
            for row in rows:
                self.tree.insert('','end',values=row)

    def left_click(self,event):
        iid = self.tree.identify_row(event.y)
        if iid:
        # mouse pointer over item
            self.tree.selection_set(iid)
            self.submenu.tk_popup(event.x_root, event.y_root)

    def show_info(self):
        string=[]
        self.txtlabel.delete(1.0,END)
        info=self.tree.focus()
        inf=self.tree.item(info)
    
        for i in range(len(self.tree['columns'])):
            new=str(inf.get('values')[i])
            string.append(new)
        
    
        self.get_description(string[0])
        image_string=self.get_image(string[1],string[0])
        self.show_image(image_string)

    def get_image(self,name,anime_id):
        url='https://myanimelist.net/anime/'+anime_id
        r = requests.get(url)
        soup = BeautifulSoup(r.content,'html.parser')
        image_parsing=soup.find_all('img',attrs={'alt': name})
        for i in range(len(image_parsing)):
            lnk = image_parsing[i]["data-src"]
        
            with open(basename(lnk),"wb") as f:
                f.write(requests.get(lnk).content)
                #print(f)
                image_string=f.name 
                return image_string     


    def get_description(self,anime_id):
    
        self.synopsis.pack(side=TOP)
        string=[]
        url='https://myanimelist.net/anime/'+anime_id
        r = requests.get(url)
        soup = BeautifulSoup(r.text,'html.parser')
        description=soup.find('p',attrs={'itemprop':'description'})
        arr=description.text.splitlines()
        for i in range(len(arr)-1):
            string.append(arr[i])
        
    
        self.txtlabel.insert(INSERT,string)
        self.txtlabel.pack(pady=20,fill='x')
    
    
    def show_image(self,string):
        self.frame3.pack(side=LEFT)
        image_tk=ImageTk.PhotoImage(Image.open(string).resize([300,300]))
    
        self.canvas.create_image(0,0,image=image_tk,anchor=NW)
        self.canvas.configure(image=image_tk)
    def delete_item(self):
        global df
        info=self.tree.focus()
        inf=self.tree.item(info)
        self.tree.delete(info)
    
        name=(inf.get('values')[0])
   
        index_names = df[ df['anime_id'] == name].index
        df.drop(index_names, inplace = True)


    def recommend_similar(self):
        
        #Focus on selected row
        info=self.tree.focus()
        #createaaray of values in row(each column is an index)
        inf=self.tree.item(info)
        #Select name(column name is second)
        new=str(inf.get('values')[1])
        
        #Base features for recommendation
        features=['genre','type']
        recommend_df=df
        
        
        for feature in features:
            recommend_df[feature] = recommend_df[feature].fillna('')
        #Combine features in new column to easily work with 
        def combined_features(row):
            return row['genre']+" "+row['type']+" "
        
        recommend_df["combined_features"] = recommend_df.apply(combined_features, axis =1)
        
        #Function to return tokens in a string
        cv=CountVectorizer()
        count_matrix=cv.fit_transform(recommend_df['combined_features'])
        
        #Apply cosine similairy to all rows
        cosine_sim = cosine_similarity(count_matrix)
        def get_index_from_title(title):
            return recommend_df[recommend_df.name == title].index.values[0]
        
        #Locate the selected anime
        anime_index = get_index_from_title(new)

        similar_animes=list(enumerate(cosine_sim[anime_index]))
        sorted_similar_animes = sorted(similar_animes, key=lambda x:x[1], reverse=True)
        def get_title_from_index(index):
            return recommend_df[recommend_df.anime_id.index == index]['name'].values[0]
        animes_recommended=[]
        i=0
        for anime in sorted_similar_animes:
            animes_recommended.append(get_title_from_index(anime[0]))
            i=i+1
            if i>15:
                break
        print(type(animes_recommended))
        rec_df=pd.DataFrame(animes_recommended,columns=['recomendation'])
        self.clear_tree2()
        #print(rec_df)
        self.tree2['column']=list(rec_df.columns)
        self.tree2['show']='headings'
        for column in self.tree2['column']:
            self.tree2.heading(column,text=column)
        rows=rec_df.to_numpy().tolist()
        
        for row in rows:
            self.tree2.insert('','end',values=row)

        self.tree2.pack()

root=Tk()
root.title("Anime app")
root.geometry('1920x1080')
app=Application(master=root)
app.mainloop()
