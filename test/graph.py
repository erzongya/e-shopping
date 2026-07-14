from langchain_core.messages import HumanMessage
from agent.graph import graph

if __name__ == "__main__":
    print("客服会话 | exit退出")
    session_state = {"messages": [], "goods_ids": [], "goods_info": []}

    while True:
        user_in = input("你：").strip()
        if user_in == "exit":
            break
        if not user_in:
            print("请输入内容\n")
            continue
        session_state["messages"].append(HumanMessage(content=user_in))
        # 极简打印执行节点
        print("执行节点：", end="")
        for update in graph.stream(session_state, config={},stream_mode="updates"):
            node = next(iter(update.keys()))
            print(node, end=" ")
        print("\n" + "-"*30)

        session_state = graph.invoke(session_state)
        print(f"客服：\n{session_state['messages'][-1].content}\n")