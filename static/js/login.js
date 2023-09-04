$(document).ready(function(){

});

function loginClick(){ // 로그인 버튼 클릭
    if($("#user_id").val() == ""){
        alert('아이디를 입력해주세요.');
        $("#user_id").focus();
        return false;
    }
    if($('#user_pw').val() == ""){
        alert('비밀번호를 입력해주세요.');
        $("user_pw").focus();
        return false;
    }
    $("#login_form").submit();
}

function signupClick(){ // 회원가입 버튼 클릭
    if($("#user_nm").val() == ""){
        alert('이름을 입력해주세요.');
        $("#user_nm").focus();
        return false;
    }
    if($("#user_id").val() == ""){
        alert('아이디를 입력해주세요.');
        $("#user_id").focus();
        return false;
    }
    if($('#user_pw').val() == ""){
        alert('비밀번호를 입력해주세요.');
        $("#user_pw").focus();
        return false;
    }
    
    if($("#user_nm").val().length <= 2){
        alert('이름은 세 글자 이상이어야 합니다. 다시 입력해주세요.');
        $("#user_nm").focus();
        return false;
    }
    if($("#user_id").val().length <= 3){
        alert('아이디는 네 글자 이상이어야 합니다. 다시 입력해주세요.');
        $("#user_id").focus();
        return false;
    }
    if($("#user_pw").val().length <= 5){
        alert('비밀번호는 여섯 글자 이상이어야 합니다. 다시 입력해주세요.');
        $("#user_pw").focus();
        return false;
    }
    $("#login_form").submit();
}