// static/js/admin.js

(function($) {
    $(document).ready(function() {
        // Şehir alanındaki değişiklikleri dinle
        $('#id_address_city').change(function() {
            var cityId = $(this).val();
            // District alanını temizle
            $('#id_address_district').empty();
            $('#id_address_area').empty();
            $('#id_address_neighborhood').empty();

            if (cityId) {
                $.ajax({
                    url: '/get_districts/', // API url'sini buraya yazmalısınız
                    data: {
                        'city_id': cityId
                    },
                    success: function(data) {
                        $('#id_address_district').append('<option value="">---------</option>');
                        $.each(data, function(index, district) {
                            $('#id_address_district').append('<option value="' + district.id + '">' + district.name + '</option>');
                        });
                    }
                });
            }
        });

        // District alanındaki değişiklikleri dinle
        $('#id_address_district').change(function() {
            var districtId = $(this).val();
            // Area ve Neighborhood alanlarını temizle
            $('#id_address_area').empty();
            $('#id_address_neighborhood').empty();

            if (districtId) {
                $.ajax({
                    url: '/get_areas/', // API url'sini buraya yazmalısınız
                    data: {
                        'district_id': districtId
                    },
                    success: function(data) {
                        $('#id_address_area').append('<option value="">---------</option>');
                        $.each(data, function(index, area) {
                            $('#id_address_area').append('<option value="' + area.id + '">' + area.name + '</option>');
                        });
                    }
                });
            }
        });

        // Area alanındaki değişiklikleri dinle
        $('#id_address_area').change(function() {
            var areaId = $(this).val();
            // Neighborhood alanını temizle
            $('#id_address_neighborhood').empty();

            if (areaId) {
                $.ajax({
                    url: '/get_neighborhoods/', // API url'sini buraya yazmalısınız
                    data: {
                        'area_id': areaId
                    },
                    success: function(data) {
                        $('#id_address_neighborhood').append('<option value="">---------</option>');
                        $.each(data, function(index, neighborhood) {
                            $('#id_address_neighborhood').append('<option value="' + neighborhood.id + '">' + neighborhood.name + '</option>');
                        });
                    }
                });
            }
        });
    });
})(django.jQuery);
