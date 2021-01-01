#!/usr/bin/env python
from flask import Flask, url_for, render_template, send_from_directory, request, flash, redirect
import jinja2.exceptions
import pickle
import pandas as pd

app = Flask(__name__)
app.secret_key = 'some_secret'

def find_all_forms_and_return_lists_and_i_and_j(unpickled_df, team_num):
    
    # 몇개의 응답이 있는지 세기 (팀별)
    completed_rows = []
    
    selected_rows_dict = unpickled_df.loc[unpickled_df['팀명'] == team_num].to_dict('records')

    for e in selected_rows_dict:

        for q_num in range(1,5):

            q_name = '질문' + str(q_num)

            if e[q_name] != "":
                # completed면 추가
                completed_rows.append(e)
                break
    
    qa_num = len(completed_rows)
    
    # for 2개니까 겉과 속 값으로 나눠주기
    i = int(qa_num/2)
    j = qa_num%2
    
    return completed_rows, i, j
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form_error')
def form_error():
    return render_template('form_error.html')

@app.route('/form_main')
def form_main():
    return render_template('form_main.html')

@app.route('/form/<teamname>', methods=['POST', 'GET'])
def form(teamname):
    
    # 피클 읽기
    unpickled_df = pd.read_pickle("./q_data.pickle")
    
    # form_write & form_update 에서 오는 POST 요청
    if request.method == 'POST':
        
        print('POST of /form', request.form)
        
        # 질문들 값 & 이름(사번) 값
        posted_form = request.form.to_dict()
        
        
        # 이름에 해당하는 Series 찾기
        selected_idx = unpickled_df.loc[unpickled_df['이름'] == posted_form['name']].index
        
        # 해당 Series에 질문값 넣어주기
        new_df = pd.DataFrame({'질문1': posted_form['q1'], 
                               '질문2': posted_form['q2'],
                               '질문3': posted_form['q3'],
                               '질문4': posted_form['q4']}, index=selected_idx)
        
        # Series에 수정 완료
        unpickled_df.update(new_df)
        
        # 수정된 Series로 피클 저장
        unpickled_df.to_pickle("./q_data.pickle")
        
        completed_rows, i, j = find_all_forms_and_return_lists_and_i_and_j(unpickled_df, int(teamname));
        
        return render_template('form.html', rows=completed_rows, numi=i, numj=j)
    
    completed_rows, i, j = find_all_forms_and_return_lists_and_i_and_j(unpickled_df, int(teamname));
        
    return render_template('form.html', rows=completed_rows, numi=i, numj=j)

# form에서 클릭 시 가는 곳 - 사번이 변수
@app.route('/form_result/<name>')
def form_result_per(name):
    
    # 기존 데이터 피클 불러오기
    unpickled_df = pd.read_pickle("./q_data.pickle")

    # 피클에서 이름(사번)값으로 Series 찾기
    selected_row_dict = unpickled_df.loc[unpickled_df['이름'] == name]
    
    if len(selected_row_dict) == 0:
        flash('이름값이 다릅니다!')
        return redirect(url_for('form_error'))
    
    selected_row_dict = selected_row_dict.to_dict('records')[0]
    
    return render_template('form_result.html', result=selected_row_dict)

@app.route('/form_result', methods=['GET', 'POST'])
def form_result():
    
    # form에서 이름(사번) 입력하면 POST로 이름(사번) 값 넘겨줌
    if request.method == 'POST':
        
        # 이름(사번)값
        posted_name = request.form.to_dict()['name']
        print('POST of /form_result', posted_name)
    
        # 기존 데이터 피클 불러오기
        unpickled_df = pd.read_pickle("./q_data.pickle")

        # 피클에서 이름(사번)값으로 Series 찾기
        selected_row_dict = unpickled_df.loc[unpickled_df['이름'] == posted_name]
        
        if len(selected_row_dict) == 0:
            print(len(selected_row_dict))
            return redirect(url_for('form_error'))

        selected_row_dict = selected_row_dict.to_dict('records')[0]
        
        # 문답 유무 체크
        check_existed = False 
        for q_num in range(1,5):
            q_name = '질문' + str(q_num)
            print(q_name)
            if selected_row_dict[q_name] != "":
                check_existed = True
                break

        ##### 이미 문답있으면 form_result로 보내기
        if check_existed:
            return render_template('form_result.html', result=selected_row_dict)
    
        ##### 문답 없으면 write로 보내기
        return render_template('form_write.html', result=selected_row_dict)
    
    return render_template('form.html')

@app.route('/form_write', methods=['GET', 'POST'])
def form_write():
    
    # form에서 이름(사번) 입력하면 POST로 이름(사번) 값 넘겨줌
    if request.method == 'POST':
        
        # 이름(사번)값
        posted_name = request.form.to_dict()['name']
        print('POST of /form_write', posted_name)
        
        # 기존 데이터 피클 불러오기
        unpickled_df = pd.read_pickle("./q_data.pickle")
        
        # 피클에서 이름(사번)값으로 Series 찾기
        selected_row_dict = unpickled_df.loc[unpickled_df['이름'] == posted_name]

        if len(selected_row_dict) == 0:
            return redirect(url_for('form_error'))

        selected_row_dict = selected_row_dict.to_dict('records')[0]
        
        # 문답 유무 체크
        check_existed = False 
        for q_num in range(1,5):
            q_name = '질문' + str(q_num)
            print(q_name)
            if selected_row_dict[q_name] != "":
                check_existed = True
                break
        
        ##### 이미 문답있으면 update로 보내기
        if check_existed:
            return render_template('form_update.html', result=selected_row_dict)
        
        ##### 문답 없으면 write로 보내기
        return render_template('form_write.html', result=selected_row_dict)

    return render_template('form.html')

@app.route('/form_update', methods=['GET', 'POST'])
def form_update():
    
    # form에서 이름(사번) 입력하면 POST로 이름(사번) 값 넘겨줌
    if request.method == 'POST':
        
        # 이름(사번)값
        posted_name = request.form.to_dict()['name']
        print('POST of /form_update', posted_name)
        
        # 기존 데이터 피클 불러오기
        unpickled_df = pd.read_pickle("./q_data.pickle")
    
        # 피클에서 이름(사번)값으로 Series 찾기
        selected_row_dict = unpickled_df.loc[unpickled_df['이름'] == posted_name]

        if len(selected_row_dict) == 0:
            return redirect(url_for('form_error'))

        selected_row_dict = selected_row_dict.to_dict('records')[0]
    
        # 기존 문답 update에서 보여면서 수정하게 하기
        return render_template('form_update.html', result=selected_row_dict)

    return render_template('form.html')
    
@app.route('/<pagename>')
def admin(pagename):
    return render_template(pagename+'.html')

@app.route('/<path:resource>')
def serveStaticResource(resource):
	return send_from_directory('static/', resource)

@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):
    return not_found(e)

@app.errorhandler(500)
def internal_error(error):
    print('Internal Server Error!')
    return render_template('form_error.html')

@app.errorhandler(404)
def not_found(e):
    print('Page Not Found!')
    return render_template('form_error.html')

if __name__ == '__main__':
    app.run()
