from django.shortcuts import render
import folium
import folium.map
import datetime
import os 
import pandas as pd


def DataEmgineering(loc_of_csv):
    df = pd.read_excel(loc_of_csv)
    latitudes = df['latitude']
    longitudes = df['longitude']
    #dateofevents = df['eventDate']
    meter_reading = df['odometer reading']
    eventgeneratedTime = df['eventGeneratedTime']
    #speed = df['speed']
    return latitudes , longitudes , meter_reading , eventgeneratedTime

def converttime(x):
    # Convert milliseconds to seconds and then to datetime
    timestamp_ms = x
    timestamp_sec = timestamp_ms / 1000
    event_date = datetime.datetime.fromtimestamp(timestamp_sec)
    # Print the event date
    return (event_date.year , event_date.month , event_date.day , event_date.hour , event_date.minute , event_date.second)

def minutes_difference(timestamp1, timestamp2):

    timestamp1 = timestamp1 / 1000
    timestamp2 = timestamp2 / 1000
    dt1 = datetime.datetime.fromtimestamp(timestamp1)
    dt2 = datetime.datetime.fromtimestamp(timestamp2)
    
    # Calculate the difference in minutes
    time_difference = abs(dt2 - dt1)
    difference_in_seconds = time_difference.total_seconds() 
        
    return difference_in_seconds

def Home(request):
    error_message = None
    threshhold = 2 #2min
    path = str(os.getcwd())
    path = os.path.join(path , 'csvfiles' , 'defaultdata.xlsx')
    name = 'defaultdata.xlsx'
    sensitivity = 0
    if request.method == 'POST':
        threshhold = float(request.POST.get('oldthreshold'))
        sensitivity = float (request.POST.get('oldsensitivity'))
        path = request.POST.get('oldpath')
        name = request.POST.get('oldname')
        try: 
                excel_file = request.FILES['excel_file']
                # Specify the path where you want to save the file on the server
                upload_folder_path = os.path.join (os.getcwd(), 'csvfiles')
                # Construct the full file path
                file_path = os.path.join(upload_folder_path , excel_file.name)
                
                # Open a new file in 'write binary' mode and write the uploaded file content to it
                with open(file_path, 'wb+') as destination:
                    for chunk in excel_file.chunks():
                        destination.write(chunk)
            
                path = file_path
                name = excel_file.name
        except:
            try:
                sensitivity = float(request.POST.get('sensitivity'))
                if request.POST.get('threshold'):
                    x = float(request.POST.get('threshold'))
                    if x < 0.001:
                        error_message = 'threshold should be greater than 1 min'
                    else:
                        threshhold = x
                elif request.POST.get('threshold') == '':
                    threshhold = float(request.POST.get('oldthreshold'))

                else:
                    error_message = 'threshold should be greater than 0.001 min'
            except:
                error_message = 'Something went wrong'
        
        
    # csv path
    
    
    #get ccsv data
    
    
    latitudes , longitudes , meter_reading , eventgeneratedTime = DataEmgineering(path)
    
    #setting threshhold make it user querryed
    #seconds
    
    
    # get map
    #centerring map
    
    m = folium.Map(location = [latitudes[0] , longitudes[0]] , zoom_start=10)
        
    #Adding End marker
    #folium.Marker([latitudes[10916] , longitudes[10916]]).add_to(m)
    
    #converting threshold from minutes to seconds
    threshhold = threshhold*60
    
    #pathpoints
    points = [[latitudes[0] , longitudes[0]]]
    
    # markedpoint
    mk = 0
    
    #stopage marker
    for k in range(len(meter_reading) - 1):
        
        if ((meter_reading[k] - meter_reading[mk]) > 10):
            points.append([latitudes[k] , longitudes[k]])
        
        # stationary almost
        if (abs(meter_reading[k] - meter_reading[k+1]) <= sensitivity):
            if (minutes_difference(eventgeneratedTime[k] , eventgeneratedTime[k+1]) > threshhold):
                reach_time_tuple=converttime(eventgeneratedTime[k]) 
                end_time_array = converttime(eventgeneratedTime[k+1])
                reach_time = f"{reach_time_tuple[0]}-{reach_time_tuple[1]}-{reach_time_tuple[2]} {reach_time_tuple[3]}:{reach_time_tuple[4]}:{reach_time_tuple[5]}"
                end_time = f"{end_time_array[0]}-{end_time_array[1]}-{end_time_array[2]} {end_time_array[3]}:{end_time_array[4]}:{end_time_array[5]}"
                StoppageDuration = int(minutes_difference(eventgeneratedTime[k] , eventgeneratedTime[k+1]))
                popup1=f"""
                        <div style="width: 200px; padding: 10px; background-color: #fff; border-radius: 5px;">
                            <h4 style="margin: 0;">Reach Time:</h4>
                            <p style="margin: 0;">{reach_time}</p>
                            <h4 style="margin: 10px 0 0 0;">End Time:</h4>
                            <p style="margin: 0;">{end_time}</p>
                            <h4 style="margin: 10px 0 0 0;">Stoppage Duration:</h4>
                            <p style="margin: 0;">{StoppageDuration} minutes</p>
                        </div>
                        """
                try:
                    folium.Marker([latitudes[k] , longitudes[k]] ,tooltip='click to See More' , popup=popup1 , 
                            max_width=500).add_to(m)
                except:
                    pass

    points.append([latitudes[len(latitudes)-5] , longitudes[len(latitudes)-5]])
    
    folium.PolyLine(points , color='black' , tooltip='Equipment Path').add_to(m)
    
    m = m._repr_html_()
    
    threshhold = float(threshhold/60)
    
    return render(request , 'core/home.html' , {'m' : m , 'error_message':error_message , 'threshold':threshhold , 'sensitivity':sensitivity , 'path':path , 'name':name})
