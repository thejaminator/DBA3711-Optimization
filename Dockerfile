FROM gurobi/optimizer:9.1.1

# remember to expose the port your app'll be exposed on.
EXPOSE 8080

RUN pip install -U pip

COPY requirements.txt app/requirements.txt
RUN pip install -r app/requirements.txt
RUN pip install -i https://pypi.gurobi.com gurobipy
RUN grbgetkey f518227c-9a3f-11eb-a577-0242ac120002

# copy into a directory of its own (so it isn't in the toplevel dir)
COPY . /app
WORKDIR /app

# run it!
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]