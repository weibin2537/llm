from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import os

# 实例化FastAPI应用
app = FastAPI(title="存储过程关系图谱API", version="1.0.0")

# 配置CORS中间件，允许所有来源、方法和头部
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# 定义图谱数据存储目录
GRAPH_DIR = "./data/processed"

@app.get("/api/graph3d")
def get_graph(
    relation: str = Query("calls", enum=["calls", "tables"], description="关系类型，calls为存储过程调用关系，tables为存储过程-表关系"),
    proc_name: str | None = Query(None, description="存储过程名称（可选，精确匹配）"),
    table_name: str | None = Query(None, description="表名称（仅在tables关系时有效，可选，精确匹配）")
):
    try:
        # 检查图谱文件是否存在
        call_graph_path = os.path.join(GRAPH_DIR, "proc_call_graph.json")
        table_graph_path = os.path.join(GRAPH_DIR, "proc_table_graph.json")
        if not os.path.exists(call_graph_path) or not os.path.exists(table_graph_path):
            return {"error": "图谱文件未找到，请确保data/processed目录下存在proc_call_graph.json和proc_table_graph.json"}, 404

        # 加载图谱数据
        call_graph = json.load(open(call_graph_path, "r", encoding="utf-8"))
        table_graph = json.load(open(table_graph_path, "r", encoding="utf-8"))
        filtered_data = {"nodes": [], "links": []}

        if relation == "calls":
            # 处理存储过程调用关系
            procs_to_process = [proc_name] if proc_name else list(call_graph.keys())
            for proc in procs_to_process:
                if proc not in call_graph:
                    continue
                # 添加当前存储过程节点
                filtered_data["nodes"].append({"id": proc, "type": "proc"})
                #处理该存储过程调用的其他存储过程
                for callee in call_graph[proc]:
                    filtered_data["nodes"].append({"id": callee, "type": "proc"})
                    filtered_data["links"].append({
                        "source": proc,
                        "target": callee,
                        "label": "调用"
                    })

        elif relation == "tables":
            # 处理存储过程与表的关系
            procs_to_process = [proc_name] if proc_name else list(table_graph.keys())
            for proc in procs_to_process:
                access_info = table_graph.get(proc, {})
                #处理读表关系
                for table in access_info.get("reads", []):
                    if table_name and table != table_name:
                        continue
                    filtered_data["nodes"].extend([
                        {"id": proc, "type": "proc"},
                        {"id": table, "type": "table"}
                    ])
                    filtered_data["links"].append({
                        "source": table,
                        "target": proc,
                        "label": "读"
                    })
                #处理写表关系
                for table in access_info.get("writes", []):
                    if table_name and table != table_name:
                        continue
                    filtered_data["nodes"].extend([
                        {"id": proc, "type": "proc"},
                        {"id": table, "type": "table"}
                    ])
                    filtered_data["links"].append({
                        "source": proc,
                        "target": table,
                        "label": "写"
                    })

        # 节点去重处理
        seen = set()
        filtered_data["nodes"] = [
            node for node in filtered_data["nodes"]
            if not (node["id"], node["type"]) in seen and not seen.add((node["id"], node["type"]))
        ]

        return {"nodes": filtered_data["nodes"], "links": filtered_data["links"]}

    except json.JSONDecodeError:
        return {"error": "图谱文件内容格式错误，请检查JSON文件"}, 400
    except Exception as e:
        return {"error": f"服务器内部错误: {str(e)}"}, 500