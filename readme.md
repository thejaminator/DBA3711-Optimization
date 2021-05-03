# Run the app
Install requirements.txt

```
pip install -r requirements.txt
pip install -i https://pypi.gurobi.com gurobipy
```

Make sure u have a [gurobi license](https://www.gurobi.com/downloads/end-user-license-agreement-academic/)
The files requirement to run the app are in the folder `project`. 
You can ignore the other folders.

Run the app
```
streamlit run app.py --server.port 80
```
