$(document).ready(function(){
    $.ajax({
        url: '/check_login',
        type: 'GET',
        success: function(response) {
            if (response.logged_in) { // 로그인 된 상태
                $("#login_button").hide();
                $("#signup_button").hide();
                $("#adminmode").show();
                $("#usermode").show();

                if(response.user_role === 'admin') {
                    $("#adminmode").show();
                } else {
                    $("#adminmode").hide();
                }

                $(".user_info_nm").text(`${response.user_nm}님`);
                $("#user_info_level").text(`Lv ${response.user_level}. ${response.user_point}점`);
                $("#user_info_review").text(`작성한 리뷰: ${response.user_review_cnt}개`);
                if(response.user_review_cnt == 0){
                    $("#cheerup_text").text("작성한 리뷰가 없어요... 리뷰를 남겨볼까요?");
                }
                else{
                    $("#cheerup_text").text("좋아요!! 더 많은 리뷰를 남겨볼까요?");
                }
                $("#hidden_login_button").hide();
            }
            else { // 로그인 안된 상태
                $("#login_button").show();
                $("#logout_button").hide();
                $("#adminmode").hide();
                $("#usermode").hide();
            }
        }
    });
});