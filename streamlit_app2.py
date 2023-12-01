import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import mysql.connector
from dateutil.relativedelta import *
import plotly.express as px
import plotly.graph_objs as go

# Function to authenticate the user
def authenticate_user(host, user, password, database='demo_database'):
    # Your MySQL database connection parameters
    try:
        # Your MySQL database connection parameters
        db_connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if db_connection.is_connected():
            return db_connection
        else:
            return False

    except mysql.connector.Error as e:
        st.error(f"An error occurred: {e}")
        return False

# Streamlit app title
st.title("Login To My DashBoard")
st.markdown(
    """
    <style>
        div[data-baseweb="input"] {
            box-shadow: 2px 2px 5px #888888;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# Streamlit login form
host = st.text_input("Host:", value = '127.0.0.1')
user = st.text_input("db_User:", value = 'root')
password = st.text_input("Password:", type="password")
database = st.text_input("db_name:", value = 'demo_database')
login_button = st.button("Login")

# Authentication logic
if login_button:
    db_connection = authenticate_user(host, user, password, database)
    if db_connection:
        st.success("Login successful!")
        st.session_state.is_authenticated = True
    else:
        st.error("Invalid credentials")

# Display authenticated content
if st.session_state.get("is_authenticated", False):
    st.title("ElectroPi Dashboard")
    db_connection = authenticate_user(host, user, password, database)
    users, admins, coupuns = st.tabs(["users", "admins", "copouns"])
    cursor = db_connection.cursor()


    with users:
        search , reg_sub, bundles, initiative,courses, grant_status, study_degree = st.tabs(["🔍 Search","Registration & Subscription", "Bundles","10k AI initiative","Courses","Grant Status","Study degree"])
        with reg_sub:
            time_interval = st.selectbox("Select Time Interval", ["Daily", "Weekly", "Monthly", "Yearly"], key = 'reg_sub')

            # Query to get registration and subscription data for subscribed = 2
            query = f"SELECT user_id, subscribed, registration_date, subscription_date FROM users;"
            cursor.execute(query)
            data = cursor.fetchall()

            df = pd.DataFrame(data, columns=["user_id", "subscribed", "registration_date", "subscription_date"])
    
            # # Convert registration_date and subscription_date columns to datetime
            df["registration_date"] = pd.to_datetime(df["registration_date"])
            df["subscription_date"] = pd.to_datetime(df["subscription_date"])
            
            if time_interval == "Daily":
                df_grouped = df.groupby(df["subscription_date"].dt.date).size().reset_index(name='count')
                df_grouped2 = df.groupby(df["registration_date"].dt.date).size().reset_index(name='count')
            elif time_interval == "Weekly":
                df_grouped = df.resample("W-Mon", on="subscription_date").size().reset_index(name='count')
                df_grouped2 = df.resample("W-Mon", on="registration_date").size().reset_index(name='count')
            elif time_interval == "Monthly":
                df_grouped = df.resample("M", on="subscription_date").size().reset_index(name='count')
                df_grouped2 = df.resample("M", on="registration_date").size().reset_index(name='count')
            elif time_interval == "Yearly":
                df_grouped = df.resample("Y", on="subscription_date").size().reset_index(name='count')
                df_grouped2 = df.resample("Y", on="registration_date").size().reset_index(name='count')
            
            st.header('User Registration & Subscription DashBoard')

            data, chart = st.tabs(["🗃 Data", "📈 Charts"])

            with chart:
                # Plotting using Plotly Express
                fig = px.line(df_grouped, x='subscription_date' if time_interval != "Yearly" else df_grouped['subscription_date'].dt.year, y='count', labels={'count': 'Number of Users'}, title=f'{time_interval} Registration & Subscriptions',color_discrete_sequence=["red"])
                fig.add_trace(px.line(df_grouped2, x='registration_date' if time_interval != "Yearly" else df_grouped2['registration_date'].dt.year, y='count').data[0])
                st.plotly_chart(fig)

            with data:

                st.subheader('number of registed users')
                df_reg = df[['registration_date']]
                df_grouped = df.groupby(df['registration_date'].dt.date).size().reset_index(name='Count' )
                df_grouped = df_grouped.sort_values(by='Count', ascending=False)
                st.dataframe(df_grouped)

                st.subheader('number of subscribed users')
                df_sub = df[df['subscribed'] ==2]['subscription_date']
              
                df_grouped2 = df.groupby(df['subscription_date'].dt.date).size().reset_index(name='Count' )
               
                df_grouped2 = df_grouped2.sort_values(by='Count', ascending=False)
                st.dataframe(df_grouped2)

                st.write("Total Registered Users:", df.shape[0])
                st.write("Total Subscribed Users:", df_grouped2["Count"].sum())
            
                st.subheader('number of subscribed users')
                df_sub = df[df['subscribed'] ==2]['subscription_date']
              
                df_grouped2 = df.groupby(df['subscription_date'].dt.date).size().reset_index(name='Count' )
               
                df_grouped2 = df_grouped2.sort_values(by='Count', ascending=False)
                st.dataframe(df_grouped2)

                st.write("Total Registered Users:", df.shape[0])
                st.write("Total Subscribed Users:", df_grouped2["Count"].sum())
        
        with bundles:
            time_interval = st.selectbox("Select Time Interval", ["Daily", "Weekly", "Monthly", "Yearly"], key = 'bundle')

           

            # Query to get subscription data
            query = '''
                SELECT u.user_id, b.bundle_name, u.subscription_date, u.subscribed 
                FROM users u
                INNER JOIN bundles b ON u.user_id = b.user_id
            '''
            cursor.execute(query)
            data = cursor.fetchall()

            df = pd.DataFrame(data, columns=["user_id", "bundle_name", "subscription_date", "subscribed"])

            start_date = min(df["subscription_date"])
            # st.write(start_date)
            if time_interval == "Daily":
                start_date = start_date - timedelta(days=1)
         
            elif time_interval == "Weekly":
                start_date = start_date - timedelta(weeks=1)
               
            elif time_interval == "Monthly":
               start_date = start_date - timedelta(days=30)
             
            elif time_interval == "Yearly":
               start_date = start_date - timedelta(days=365)
             
            # Convert subscription_date column to datetime
            df["subscription_date"] = pd.to_datetime(df["subscription_date"])

            if time_interval == "Daily":
                df_grouped = df.groupby(df["subscription_date"].dt.date).size()
            elif time_interval == "Weekly":
                df_grouped = df.set_index("subscription_date").resample("W").size()
            elif time_interval == "Monthly":
                df_grouped = df.set_index("subscription_date").resample("M").size()
            elif time_interval == "Yearly":
                df_grouped = df.set_index("subscription_date").resample("Y").size()


            data, chart = st.tabs(["🗃 Data", "📈 Charts"])

            with chart :

                st.subheader(f"{time_interval} Subscriptions by Bundle")
                st.line_chart(df_grouped)

                st.subheader("number of user subscribed to each bundle")
                st.bar_chart(df["bundle_name"].value_counts())
            
            with data:

                # Display the raw data
                st.write("### Raw Data")
                st.dataframe(df_grouped.rename("Count"))

                for bundle in df["bundle_name"].unique():
                    bundle_count = df[df["bundle_name"] == bundle].shape[0]
                    st.write(f"{bundle}: {bundle_count}")
                st.write("Total Subscriptions:", df.shape[0])
        
        with initiative:
            query = '''
                SELECT u.user_id,
                    (
                        SELECT COUNT(ucc_inner.course_id)
                        FROM user_completed_courses ucc_inner
                        WHERE ucc_inner.user_id = u.user_id
                    ) AS completed_course_count,
                    (
                        SELECT MAX(ucc_inner.completion_date)
                        FROM user_completed_courses ucc_inner
                        WHERE ucc_inner.user_id = u.user_id
                    ) AS last_completed_date,
                    (
                        SELECT ucc_inner.course_degree
                        FROM user_completed_courses ucc_inner
                        WHERE ucc_inner.user_id = u.user_id
                        ORDER BY ucc_inner.completion_date DESC
                        LIMIT 1
                    ) AS last_completed_degree
                FROM users u
                WHERE u.10k_AI_initiative = 1
            '''

            cursor.execute(query)
            data = cursor.fetchall()


            df = pd.DataFrame(data, columns=["user_id", "completed_course_count", "last_completed_date", "last_completed_degree"])
            st.subheader("10k AI Initiative User Dashboard")
            df_sorted = df.sort_values(by='completed_course_count', ascending=False)
          

            data, chart = st.tabs(["🗃 Data", "📈 Charts"])

            with chart:
                # st.subheader("Completed Courses for each user")
                # st.bar_chart(df.set_index("user_id")["completed_course_count"])

                # st.subheader("Last Completed Course Degrees")
                # st.bar_chart(df.set_index("user_id")["last_completed_degree"])

                # st.subheader("Last Completed Course Dates")
                # st.bar_chart(df.set_index("user_id")["last_completed_date"])

                grouped_df = df.groupby('completed_course_count').size().reset_index(name='count')
                grouped_df['completion_percentage'] = (grouped_df['count'] / grouped_df['count'].sum()) * 100

                # Create an interactive bar chart with Plotly
                fig = px.bar(grouped_df, x='completed_course_count', y='completion_percentage', text='completion_percentage',
                            labels={'completion_percentage': 'Completion Percentage'},
                            title='Percentage of Completed Courses',
                            height=500)

                # Customize the layout
                fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                fig.update_layout(xaxis_title='Completed Course Count', yaxis_title='Completion Percentage', showlegend=False)
                st.plotly_chart(fig)

                bins = [0, 69, 79, 89, 100]
                labels = ['<70', '70-79', '80-89', '>=90']

                # Create a new column with the degree ranges
                df['degree_range'] = pd.cut(df['last_completed_degree'], bins=bins, labels=labels, right=False)

                # Group by degree_range and calculate the sum
                grouped_df = df.groupby('degree_range').size().reset_index(name='count')
                grouped_df['completion_percentage'] = (grouped_df['count'] / grouped_df['count'].sum()) * 100

                # Create an interactive bar chart with Plotly
                fig = px.bar(grouped_df, x='degree_range', y='completion_percentage', text='completion_percentage',
                            labels={'completion_percentage': 'Completion Percentage'},
                            title='Percentage Last Completed Degree',
                            height=500)

                # Customize the layout
                fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                fig.update_layout(xaxis_title='Last Completed Degree Range', yaxis_title='Completion Percentage', showlegend=False)
                st.plotly_chart(fig)
            

            with data : 
                st.subheader("10K initiative users")
                st.dataframe(df_sorted)
            
                st.markdown(f'Number of users in the 10k AI initiative: :red[{len(df_sorted)}]')

        with courses:

            st.header("User Learning and Completion Dashboard")
            time_interval = st.selectbox("Select a time frame ", ["this Week", "this Month", "this Year"], key = 'courses')

            currently_learning_query = '''
                SELECT uc.user_id, COUNT(uc.course_id) as learning_courses
                FROM user_courses uc
                LEFT JOIN user_completed_courses ucc ON uc.user_id = ucc.user_id AND uc.course_id = ucc.course_id
                WHERE ucc.user_id IS NULL
                GROUP BY uc.user_id
            '''

            if time_interval == "this Week":
                completed_courses_query = '''
                    SELECT ucc.user_id, COUNT(ucc.course_id) as completed_courses
                    FROM user_completed_courses ucc
                    WHERE YEARWEEK(ucc.completion_date) = YEARWEEK(NOW())
                    GROUP BY ucc.user_id
                '''
            elif time_interval == "this Month":
                completed_courses_query = '''
                    SELECT ucc.user_id, COUNT(ucc.course_id) as completed_courses
                    FROM user_completed_courses ucc
                    WHERE YEAR(ucc.completion_date) = YEAR(NOW()) AND MONTH(ucc.completion_date) = MONTH(NOW())
                    GROUP BY ucc.user_id
                '''
            else:
                completed_courses_query = '''
                    SELECT ucc.user_id, COUNT(ucc.course_id) as completed_courses
                    FROM user_completed_courses ucc
                    WHERE YEAR(ucc.completion_date) = YEAR(NOW())
                    GROUP BY ucc.user_id
                '''

            cursor.execute(currently_learning_query)
            currently_learning_data = cursor.fetchall()

            cursor.execute(completed_courses_query)
            completed_courses_data = cursor.fetchall()

            currently_learning_df = pd.DataFrame(currently_learning_data, columns=["user_id", "learning_courses"])
            completed_courses_df = pd.DataFrame(completed_courses_data, columns=["user_id", "completed_courses"])

            user_data = currently_learning_df.merge(completed_courses_df, on="user_id", how="left")

            user_data["completed_courses"].fillna(0, inplace=True)

            data, chart = st.tabs(["🗃 Data", "📈 Charts"])

            with data :
                st.subheader(f"Number of completed courses {time_interval}")
                user_data_sorted = user_data.sort_values(by='completed_courses', ascending=False)
                st.dataframe(user_data_sorted)
            
            with chart :
                st.subheader(f"Number of Completed Courses {time_interval}")
                # st.bar_chart(user_data.set_index("user_id")["completed_courses"])
                grouped_df = user_data.groupby('completed_courses').size().reset_index(name='count')
                grouped_df['completion_percentage'] = (grouped_df['count'] / grouped_df['count'].sum()) * 100

                # Create an interactive bar chart with Plotly
                fig = px.bar(grouped_df, x='completed_courses', y='completion_percentage', text='completion_percentage',
                            labels={'completion_percentage': 'Completion Percentage'},
                            title=f'Percentage of Completed Courses {time_interval}',
                            height=500)

                # Customize the layout
                fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
                fig.update_layout(xaxis_title='Completed Course Count', yaxis_title='Completion Percentage', showlegend=False)
                st.plotly_chart(fig)

        with search:

            user_id = st.text_input("", "Search by User ID")
            search_button = st.button("Search")
            if search_button:
                try:
                    user_id = int(user_id)

                    users_data = f'''
                        SELECT * FROM users WHERE user_id = {user_id}
                    '''
                    cursor.execute(users_data)
                    users_data = cursor.fetchall()

                    if not users_data:
                        st.warning(f"No user found with user_id: {user_id}")
                    else:
                        # Display the user data as a DataFrame
                        users_data_df = pd.DataFrame(users_data, columns=["user_id", "subscribed", "subscription_date",
                                                                        "coupon", "registration_date", "last_edit_date",
                                                                        "level", "gender", "age", "study_degree",
                                                                        "10k_AI_initiative"])
                        st.header("User's DashBoard")
                        st.write(users_data_df)

                        st.subheader("User's Bundles")
                        bundles_query = f"SELECT bundle_id, bundle_name FROM bundles WHERE user_id = {user_id}"
                        cursor.execute(bundles_query)
                        bundles_data = cursor.fetchall()

                        if bundles_data:

                            bundle_data  = pd.DataFrame(bundles_data,columns=['bundle_id','bundle_name'])
                            for col in bundle_data.columns:
                                st.write(f'{col}: ',bundle_data[col][0])

                        else :
                            st.markdown(':red[user not subscribed to any bundle]')

                        st.subheader("User's Cousres")

                        course_query = f'''
                        SELECT uc.* ,c.title 
                        FROM user_courses uc, courses c
                        WHERE uc.course_id = c.course_id
                        and uc.user_id = {user_id};
                        '''

                        cursor.execute(course_query)
                        courses_data = cursor.fetchall()

                        if courses_data:

                            courses_data  = pd.DataFrame(courses_data,columns=['usere_id','course_id','chapter_id','lesson_id','course_name'])
                            st.write(courses_data)
                            st.write('number of courses :', len(courses_data))

                        else :
                            st.write(':red[no courses available]')

                            
                        st.subheader('Complted Courses')

                        completed_courses_query = f'''
                        SELECT ucc.user_id, ucc.course_id, ucc.course_degree ,ucc.completion_date, c.title
                        FROM user_completed_courses ucc, courses c
                        where ucc.course_id = c.course_id
                        and  ucc.user_id = {user_id};

                        '''

                        cursor.execute(completed_courses_query)
                        completed_courses_data = cursor.fetchall()

                        if completed_courses_data:
                            completed_courses_data  = pd.DataFrame(completed_courses_data,columns=['usere_id','course_id','course_degree','complation_date','course_name'])
                            st.write(completed_courses_data.iloc[:,1:])
                            st.write('number of complated courses :', len(completed_courses_data))
                        else :
                            st.write('No Courses Completed')
                        

                        st.subheader("User's Capstones")
                        capstones_query = f'''
                        SELECT * 
                        FROM capstones 
                        WHERE user_id = {user_id}
                        and degree > 50;
                        '''
                        cursor.execute(capstones_query)
                        completed_capstones = cursor.fetchall()
                        if completed_capstones:
                            completed_capstones  = pd.DataFrame(completed_capstones,columns=['usere_id','course_id','chapter_id','lesson_id','degree','lock','last_submission_date','reviewed','revision_date'])
                            st.write(completed_capstones.iloc[:,1:])
                            st.write('number of complated capstones :', len(completed_capstones))
                        else :
                            st.write(':red[No Capstones available]')
                        
        

                        # Query to get users' capstone information and evaluation history
                        capstone_evaluation_query = f'''
                        SELECT c.user_id, c.course_id,  eh.degree as capstone_degree, c.revision_date, eh.evaluation_date,c.reviewed,eh.admin_id
                        FROM capstones c,  capstone_evaluation_history eh 
                        where eh.user_id ={user_id} AND c.course_id = eh.course_id and c.revision_date = eh.evaluation_date
                        order by c.user_id, c.revision_date;
                        '''

                        cursor.execute(capstone_evaluation_query)
                        capstone_evaluation_data = cursor.fetchall()

                        # Create a DataFrame from the fetched data
                        capstone_evaluation_df = pd.DataFrame(capstone_evaluation_data, columns=[
                            "user_id", "course_id", "capstone_degree", "revision_date", "evaluation_date","reviewed","admin_id"
                        ])

                        # Display users' capstone information and evaluation history
                        st.subheader("Capstones Evaluation History")
                        capstone_evaluation_df = capstone_evaluation_df.sort_values(by = ['course_id','evaluation_date'])
                        st.write(capstone_evaluation_df)
                        # st.subheader('users drgree in each capstone')
                        # capstones = capstone_evaluation_df['course_id'].unique()
                        # capston = []
                        # for i in capstones:
                        #     capston.append(i)
                        
                        # capston = st.selectbox('select capstone :',capston)
                        
                        # if capston:
                        #     st.subheader('Users degrees in this capstone')
                        #     df = capstone_evaluation_df[capstone_evaluation_df['course_id'] == capston]
                        #     # st.bar_chart((df.set_index('user_id')['capstone_degree']))
                        #     fig = px.bar(
                        #         df,
                        #         x="user_id",
                        #         y="capstone_degree",
                        #         # color="revision_date",
                        #         labels={"capstone_degree": "Capstone Degree", "user_id": "User ID", "revision_date": "Revision Date"},
                        #         title="Capstone Degrees of Each User"
                        #     )

                        #     # Show the Plotly chart using Streamlit
                        #     st.plotly_chart(fig)

            

                except ValueError:
                    st.error("Please enter a valid User ID")            

        with grant_status:
            user_employment_grant_query = f'''
            SELECT user_id ,status, application_date
            FROM users_employment_grant;
            '''
            st.header('users Employment Grant Status DashBoard')
            cursor.execute(user_employment_grant_query)
            user_employment_grant_data = cursor.fetchall()
            user_employment_grant_data_df = pd.DataFrame(user_employment_grant_data, columns=["user_id", "status", "application_date"])

           

            # Count of users in each employment grant status
            status_counts = user_employment_grant_data_df["status"].value_counts()

            # Create a bar chart to visualize the count of users in each employment grant status
            data, chart = st.tabs(["🗃 Data", "📈 Charts"])

            with chart:

                st.subheader("Count of Users in Each Employment Status")
                st.bar_chart(status_counts)

           
            # st.write(user_employment_grant_data_df)
            with data :
                st.markdown("all Users in Employment Grant")
                st.write(user_employment_grant_data_df)
                st.subheader('User Employment Grant Action')
                action = st.selectbox("Select Users Status", ["submitted", "prepration", "pending", "hold",'interview', 'shortlisted','postponed','accepted'])

                user_employmenr_action_query = f'''
                SELECT * 
                FROM users_employment_grant_actions
                '''
                cursor.execute(user_employmenr_action_query)
                user_employment_action_data = cursor.fetchall()

                user_employment_action_data = pd.DataFrame(user_employment_action_data,columns=['user_id',"submitted", "prepration", "pending", "hold",'interview', 'shortlisted','postponed','accepted'])

                if action == 'submitted':
                    df = user_employment_action_data[user_employment_action_data['submitted'].notnull()]
                    st.dataframe(df)
                    st.write('number of users in submitted stage : ', len(df))

                elif action == 'prepration':
                    df = user_employment_action_data[user_employment_action_data['prepration'].notnull()]
                    st.dataframe(df)
                    st.write('number of users in prepration stage : ', len(df))

                elif action == 'pending':
                    df = user_employment_action_data[user_employment_action_data['pending'].notnull()]
                    st.dataframe(df)
                    st.write('number of users in pending stage : ', len(df))

                elif action == 'hold':
                    df = user_employment_action_data[user_employment_action_data['hold'].notnull()]
                    st.dataframe(df)
                    st.write('number of users in hold stage : ', len(df))

                elif action == 'interview':
                    df = user_employment_action_data[user_employment_action_data['interview'].notnull()]
                    st.dataframe(df)
                    st.write('number of users in interview stage : ', len(df))

                elif action == 'shortlisted':
                    df = user_employment_action_data[user_employment_action_data['shortlisted'].notnull()]
                    st.dataframe(df)
                    st.write('number of users in shortlisted stage : ', len(df))

                elif action == 'postponed':
                    df = user_employment_action_data[user_employment_action_data['postponed'].notnull()]
                    st.dataframe(df)
                    st.write('number of users in postponed stage : ', len(df))

                elif action == 'accepted':
                    df = user_employment_action_data[user_employment_action_data['accepted'].notnull()]
                    st.dataframe(df)
                    st.write('number of users in accepted stage : ', len(df))
        
        with study_degree:
             # Query to fetch the number of users grouped by age and study degree
            users_grouped_query = '''
                SELECT age, study_degree, COUNT(user_id) as user_count
                FROM users
                GROUP BY age, study_degree
            '''

            cursor.execute(users_grouped_query)
            users_grouped_data = cursor.fetchall()

            # Create a DataFrame from the fetched data
            users_grouped_df = pd.DataFrame(users_grouped_data, columns=["age", "study_degree", "user_count"])

            st.header("Users Age and Study Degree Dashboard")

            data, chart = st.tabs(["🗃 Data", "📈 Charts"])
            with data:
                st.dataframe(users_grouped_df)

            with chart :
            #     st.subheader(f"Number of Users Grouped by Age and Study Degree")
            
            #     fig = px.bar(users_grouped_df, x="study_degree", y="user_count", color="age", barmode="group")

            # st.plotly_chart(fig)
                fig = px.bar(users_grouped_df, x='age', y='user_count', title='Number of Users Grouped by Age',
                            labels={'user_count': 'Number of Users', 'age': 'Age'})

                # Showing the plot
                st.plotly_chart(fig)

                # fig2 = px.bar(users_grouped_df, x='study_degree', y='user_count', title='Number of Users Grouped by study degree',
                #              labels={'user_count': 'Number of Users', 'study_degree': 'Study Degree'})

                # # Showing the plot
                # st.plotly_chart(fig2)

                total_users = users_grouped_df['user_count'].sum()
                users_grouped_df['percentage'] = (users_grouped_df['user_count'] / total_users) * 100

                # Creating a pie chart using Plotly Express
                fig3 = px.pie(users_grouped_df, names='study_degree', values='percentage',
                            title='Percentage Distribution of Users by Study Degree',
                            labels={'percentage': 'Percentage', 'study_degree': 'Study Degree'})

                # Showing the plot
                st.plotly_chart(fig3)

                
    with admins:
        

        # Query to get the number of capstones evaluated for each admin
        capstones_evaluated_query = f'''
        SELECT a.admin_id,
            SUM(CASE WHEN DATE(c.evaluation_date) = CURDATE() THEN 1 ELSE 0 END) AS today_evaluations,
            SUM(CASE WHEN YEARWEEK(c.evaluation_date, 1) = YEARWEEK(NOW(), 1) THEN 1 ELSE 0 END) AS this_week_evaluations,
            SUM(CASE WHEN DATE_FORMAT(c.evaluation_date, '%Y-%m') = DATE_FORMAT(NOW(), '%Y-%m') THEN 1 ELSE 0 END) AS this_month_evaluations
        FROM capstone_evaluation_history c
        JOIN admins a ON c.admin_id = a.admin_id
        GROUP BY a.admin_id;
        '''
        cursor.execute(capstones_evaluated_query)
        admin_evaluation_data = cursor.fetchall()
    

    
        st.header("Admin Capstone Evaluation Dashboard")

        # Display admin evaluation data
        data, chart = st.tabs(["🗃 Data", "📈 Charts"])
        with data:

            admin_evaluation_df = pd.DataFrame(admin_evaluation_data, columns=["admin_id", "today_evaluations", "this_week_evaluations", "this_month_evaluations"])
            st.write(admin_evaluation_df)
        
        with chart:
            # Create bar charts to visualize capstone evaluations for each admin
            trace_today = go.Bar(x=admin_evaluation_df['admin_id'], y=admin_evaluation_df['today_evaluations'], name='Today')
            trace_week = go.Bar(x=admin_evaluation_df['admin_id'], y=admin_evaluation_df['this_week_evaluations'], name='This Week')
            trace_month = go.Bar(x=admin_evaluation_df['admin_id'], y=admin_evaluation_df['this_month_evaluations'], name='This Month')

            # Combine traces into a single figure
            fig = go.Figure(data=[trace_today, trace_week, trace_month])

            # Update layout to include axis labels and a title
            fig.update_layout(
                barmode='group',
                xaxis=dict(title='Admin ID'),
                yaxis=dict(title='Number of Capstone Evaluations'),
                title='Capstone Evaluations by Admin'
            )

            # Display the figure using Plotly in Streamlit
            st.plotly_chart(fig)


    with coupuns:
        coupons_query = '''
        SELECT c.copon_code, COUNT(u.user_id) as used_by_users
            FROM copons c
            LEFT JOIN users u ON c.copon_code = u.coupon
            GROUP BY c.copon_code
        '''

        cursor.execute(coupons_query)
        coupons_data = cursor.fetchall()

        # Create a DataFrame from the fetched data
        coupons_df = pd.DataFrame(coupons_data, columns=["coupon_code", "used_by_users"])
        st.header("Coupon Usage Dashboard")
        data, chart = st.tabs(["🗃 Data", "📈 Charts"])
        with data:
            # Display coupon usage data
            st.dataframe(coupons_df)
        with chart:
            # Create bar chart to visualize the number of users who used each coupon
            st.subheader(f"Number of Users Who Used Each Coupon")
            st.bar_chart(coupons_df.set_index("coupon_code")["used_by_users"])
        

    cursor.close()
    db_connection.close()
    
