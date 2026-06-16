import streamlit as st

st.title(" 안녕!! 유지아 👋")
st.markdown(
    """ 
    사랑하는 유지아~~~. 

    **오늘도 :rainbow[고생했어요]**
    
    아빠 오늘 회식이야~~~ 일찍갈께~~~~
    **:rainbow[사랑해]** 
    """
)

if st.button("여기 눌러줘!"):
    st.balloons()