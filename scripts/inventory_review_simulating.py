# Giả lập cột shelf_life
def assign_shelf_life (item_id):
    try:
        item_num = int("".join(filter(str.isdigit, str(item_id))))
    except:
        item_num = 1
    
    if item_num <= 15:
        return 7
    elif item_num <= 30:
        return 14
    else:
        return 30
df['shelf_life_days'] = df['item_id'].apply(assign_shelf_life)


# Tạo cột is_review_date
def check_review_date (row):
    day_of_week = row['date_calendar'].dt.dayofweek if hasattr (row['date_calendar'],'dt') else pd.Timestamp(row['date_calendar']).dayofweek
    shelf_life = row['shelf_life_days']
    if shelf_life == 7:
        return day_of_week in [0,2,4]
    elif shelf_life == 14:
        # Nếu thứ của ngày đang được xét rơi vào 0,2,4 trả về True, không thì trả về False
        return day_of_week in [0,3]
    
    else:
        return day_of_week in [0,3]
df['is_review_date'] = df.apply(check_review_date, axis = 1)

#df['is_reviewdate'] = để tạo một cột mới trong dataframe
# df['date_calendar'] truy cập vào cột date_calendar
# .dt công cụ Accessor của Pandas, kích hoạt các tính năng chuyên biệt để xử ký dữ liệu thời gian
# .dayofweek chuyển đổi dữ liệu ngày thành thứ trong tuần, 0 là thứ hai, 6 là chủ nhật.
# .isin([0,3]) kiểm tra xem dữ liệu trong df['date_calendar'].dt.dayofweek có khớp với số nào trong danh sách không nếu khớp trả về True, ngược lại là False

def generate_lead_time (rows):
    # def generate_lead_time (abc_category) để tạo hàm, abc_category là tham số (x) được truyền vào hàm
    abc_category = rows['abc_category']
    shelf_life = rows['shelf_life_days']

    if shelf_life in [7,14]:
        return np.random.choice ([1,2], p = [0.4, 0.6])
    else:
        if abc_category == 'A' :
            return np.random.choice ([1,2], p = [0.4, 0.6])
        # np.random.choice ([1,2], p=[0.4, 0.6]) lựa chọn ngẫu nhiên giá trị trong danh sách.
        # p=[0.4, 0.6]) xác suất 1 xuất hiện là 40% và 2 là 60%
        elif abc_category == 'B':
            return np.random.choice ([2,3,4], p = [0.2, 0.6, 0.2])
        else :
            return np.random.choice ([4,5,7], p = [0.5, 0.3, 0.2])
    
# Áp dụng cho từng dòng dựa trên cột
df['assumed lead time'] = df.apply(generate_lead_time, axis = 1)

def generate_fill_rate (abc_category):
    """
    Giả lập tỷ lệ đáp ứng đơn hàng (Fill Rate) dựa trên phân lớp mặt hàng ABC.
    Trả về một số thực từ 0.0 đến 1.0 đại diện cho tỷ lệ lượng hàng thực nhận.
    """
    if abc_category == 'A':
        # Nhóm A: 98% cơ hội giao đủ 100%, 2% cơ hội giao thiếu một ít (từ 90%-98%)
        return np.random.choice(
            [1.0, np.random.uniform(0.90, 0.98)],
            p=[0.98, 0.02]
        )
    elif abc_category == 'B':
        # Nhóm B: 93% giao đủ, 6% giao thiếu (từ 75% - 90%), 1% hủy đơn hoàn toàn (0.0)
        return np.random.choice (
            [1.0, np.random.uniform(0.75, 0.90), 0.0],
            p = [0.93, 0.06, 0.01]
        )
    else:
        # Nhóm C: 85% giao đủ, 12% giao thiếu nhiều (từ 50% - 80%), 3% hủy đơn hoàn toàn (0.0)
        return np.random.choice (
            [1.0, np.random.uniform(0.50, 0.80), 0.0],
            p=[0.85, 0.12, 0.03]
        )
    
df['assumed_fill_rate'] = df['abc_category'].apply(generate_fill_rate)
    



# %%

# =======================================================
# 
# =======================================================






# =======================================================
# TẠO HÀM GIẢ LẬP ĐỂ TÍNH TOÁN THEO NHÓM STORE-ITEM
# =======================================================


def calculate_by_group(group): 

    # -------------------------------------------------------
    # LƯU CỘT DỮ LIỆU ĐƯỢC GROUP
    # -------------------------------------------------------
    # Lệnh isinstance (value, datatype) được dùng để kiểm tra kiểu dữ liệu
    # Mục đích đoạn code if - else này để tránh sập cả đoạn code nếu groupby chỉ nhóm theo một cột.
    # Nếu bạn chắc chắn group theo 2 cột trở lên bạn chỉ cần dùng câu lệnh current_store = group.name[0]
    if isinstance(group.name, tuple): # Nếu group bằng 2 cột, group.name sẽ ở định dạng tuple
        # group.name[0] để trả về giá trị ở stt 0 trong tuple, nếu nhóm 2 cột là store_id và item_id, tuple sẽ là ('store_id', 'item_id'). group.name[0] sẽ trả về kết quả 'store_id'
        # Ví dụ cột store chưa dữ liệu store_1, store_2, store_3. Khi lệnh groupby chạy, group theo cột store, nhóm store_1 sẽ được chạy trước lúc này group.name[0] sẽ là store_1 và lần lượt đến store_2...
        current_store = group.name[0] # Lưu trước tên của cột được nhóm, tránh làm mất dữ liệu cột khi python thực hiện group và xóa index để làm sạch bản.
        current_item = group.name[1]  # Sau khi lưu tên cột, dùng group[store_id] = current_store để lấy lại cột mất.
    
    else: # Nếu group bằng 1 cột group.name sẽ ở định dạng int hoặc str chứ không phải tuple
        # Nhánh này chạy khi gộp ĐƠN CỘT (hoặc các trường hợp đặc biệt khác)
        # Lúc này group.name KHÔNG PHẢI tuple, nên lệnh group.name[0] sẽ bị lỗi hoặc lấy sai ký tự đầu tiên
        # Do đó code phải đổi chiến thuật, nhìn trực tiếp vào cột phẳng để bốc dữ liệu:
        current_store = group['store_id'].iloc[0] if 'store_id' in group.columns else None
        current_item = group['item_id'].iloc[0] if 'item_id' in group.columns else None




    # ======================================================================================
    # CHUẨN BỊ THÀNH PHẦN CẦN THIẾT ĐỂ CHẠY VÒNG LẶP
    # ======================================================================================


    # -------------------------------------------------------
    # TẠO MẢNG NUMPY VÀ RESET CHỈ MỤC
    # -------------------------------------------------------

    # Bây giờ bốc giá trị từ cột phẳng ra cực kỳ an toàn
    # Reset chỉ mục nội bộ của dataframe con về từ 0 đến N-1 để tính toán ngày chính xác
    # Nếu không reset chỉ mục, dataframe con sẽ lấy chỉ mục từ df chính, làm chỉ mục lộn xộn dẫn đến tính toán sai lệch
    group = group.reset_index(drop=True)
    N = len(group)

    # Tạo mảng mới, đẩy các cột cần tính toán xuống tầng numpy để tăng hiệu suất.
    demand_array = group['new_tsl'].to_numpy()
    sales_array = group['sales'].to_numpy()
    fill_rate_array = group['assumed_fill_rate'].to_numpy()
    lead_time_array = group['assumed lead time'].to_numpy()

    # vì mỗi group có cùng một hạn sử dụng nên ta thiết lập hạn sử dụng tĩnh ngay từ đầu để tránh trích xuất từng dòng khi xét điều kiện ở đoạn code sau
    shelf_life_days = int(group['shelf_life_days'].loc[0])

    date = group['date_calendar'].dt.date
    dates_array = date.to_numpy()

    # Xác định chu kì kiểm kho R thực tế cho mỗi nhóm
    if shelf_life_days == 7:    
        R = 1.0
    elif shelf_life_days == 14:
        R = 2.3 # Khoảng cách trung bình giữa T2, T4, T6
    elif shelf_life_days == 30:
        R = 3.5



    # -------------------------------------------------------
    # CHUẨN BỊ MẢNG TRỐNG
    # -------------------------------------------------------


    # Khởi tạo trước các mảng để ghi dữ liệu
    rop_dynamic = np.zeros (N)
    tsl_dynamic = np.zeros (N)
    on_hand = np.zeros(N)
    order_qty = np.zeros(N)
    inventory_position = np.zeros(N)

    expired_log = np.zeros(N)

    arrival_date = {}
    lead_time_history = {}

    inventory_batches = []
    
    
    


    # -------------------------------------------------------
    # CHUẨN BỊ CHO NGÀY ĐẦU TIÊN TRƯỚC KHI CHẠY VÒNG LẶP
    # -------------------------------------------------------


    # Xác định ngày kiểm kho ĐẦU TIÊN xuất hiện trong chuỗi của cụm này
    # group['is_review_date'] là lấy cột is_review_date trong bản con, group[group['is_review_date'] là chỉ lấy giá trị True. .index sẽ là lấy chỉ mục của các giá trị True đó
    review_indicies = group[group['is_review_date']].index

    # Câu lệnh if len (review_indicies) > 0 else -1 là để bảo vệ đoạn code tránh trường hợp, một nhóm store - item không có ngày xét kho nào, -1 là để đánh dấu bất thường mở đường cho đoạn code if first_review_date = -1 thì bỏ qua không tính nữa
    first_review_idx = review_indicies[0] if len (review_indicies) > 0 else -1

    # Đoạn code này sẽ làm việc tính toán dừng ngay lập tức nếu df con không có ngày kiểm tra hàng
    if first_review_idx == -1:
        group['rop'] = rop_dynamic
        group['tsl'] = tsl_dynamic
        group['on_hand'] = on_hand
        group['inventory_position']= inventory_position
        group['order_qty'] = order_qty
        group['store_id'] = current_store
        group['item_id'] = current_item
        return group
    

    # Câu lệnh if N > 0 được tạo ra nhằm mục đích:
    #   + Để khởi tạo ngày 0 làm tiền đề cho vòng lặp để bắt đầu i>0 mà không cần đưa ngày 0 vào vòng lặp, vì ở ngoài vòng lặp thì nó chỉ cần chạy một lần, nếu trong vòng lặp nó phải lặp đi lặp lại nhiều lần if i==0
    #   + Chốt chặn an toàn tránh sập code, khi thực hiện nhóm theo store, item có thể tồn tại một số mặt hàng rỗng, không có dữ liệu bán hàng, nếu python quét on_hand[0] thấy tập dữ liệu rỗng nó sẽ trả về lỗi.
    if N >0:
        
         # TÍNH TOÁN LƯỢNG HÀNG CHO NGÀY ĐẦU TIÊN

        # Điểm bắt đầu để cắt mảng và cho vào list 
        start_idx_first = first_review_idx + 1
        

        # Chia nhánh: nếu hxd là 7 hoặc 14 ngày thì tsl coverage = R + L, nếu 30 ngày thì 2R + L    
        if shelf_life_days in [7,14]:
            first_tsl_coverage = int(R + int(group.loc[first_review_idx, 'assumed lead time']))
        else:
            first_tsl_coverage = int(2 * R + int(group.loc[first_review_idx, 'assumed lead time']))


        end_point_tsl = start_idx_first + 7
        first_tsl_list = demand_array[start_idx_first : end_point_tsl]
        actual_first_tsl = 0
        for k in range(first_tsl_coverage):
            future_weekday =  k % 7
            weekday_tsl = first_tsl_list[future_weekday]
            actual_first_tsl += weekday_tsl
        
        # actual_first_tsl = cumsum_demand[tsl_end_first] - cumsum_demand[start_idx_first]
            
        # Đổ đầy kho ngày đầu bằng đúng con số TSL thực tế này
        on_hand[0] = actual_first_tsl

        # NẠP LÔ HÀNG ĐẦU TIÊN: coi như lượng hàng ban đầu có hạn dùng tối đa từ ngày 0
        if on_hand[0] > 0:
            inventory_batches.append({
                'qty': int(on_hand[0]),
                'exp': dates_array[0] + pd.Timedelta( days= shelf_life_days)
            })
        last_rop = 0
        last_tsl = 0
    



    # =======================================================
    # CHẠY VÒNG LẶP
    # =======================================================


    for i in range(N):
        current_date = dates_array[i]


        # -------------------------------------------------------
        # KIỂM TRA TRẠNG THÁI KHO NGÀY TẤT CẢ CÁC NGÀY
        # -------------------------------------------------------
        

        # -------------------------------------------------------
        # 1. XỬ LÝ ĐẦU NGÀY: KIỂM TRA VÀ TIÊU HỦY HÀNG HẾT HẠN
        # -------------------------------------------------------


        today_expired_qty = 0
        active_batches = []

        for batch in inventory_batches:
            if batch['exp'] <= current_date:
                today_expired_qty += batch['qty']
            else:
                # Tại sao ở đây cần dùng điều kiện batch['qty'] > 0 trong khi đoạn code xuất và khấu trừ ở dưới đã làm sạch batch = 0 ?
                # Vì nguyên tắc đảm bảo tính độc lập và toàn vẹn của từng bước trong thiết kế thuật toán, mỗi khối chức năng nên tự chịu trách nhiệm làm sạch dữ liệu của chính nó.
                if batch['qty'] > 0:
                    active_batches.append(batch)
        
        inventory_batches = active_batches
        expired_log[i] = today_expired_qty # Ghi nhận số lượng hủy của ngày i




        # -------------------------------------------------------
        # 2. XỬ LÝ NHẬN HÀNG CẬP BẾN (INBOUND IN THE MORNING)
        # -------------------------------------------------------


        # Thêm hàng vào kho nếu cập bến
        incoming_goods = arrival_date.get(i,0) # dùng get(key,0) để tra key và lấy giá trị gắn với key trong Dictionary, nếu không tìm thấy key trả về 0
        if incoming_goods > 0:
            # Hàng THỰC SỰ về kho ngày hôm nay -> Tạo lô mới tình từ hôm nay
            # Dùng .Timedelta để cộng ngày đảm bảo expiry_date được tính toán đúng. Nếu dùng i thay vì ngày, i sẽ bỏ qua các ngày cửa hàng không mở và tiếp tục ghi nối liền, làm cho việc tính toán expiry date bị lệch.
            expiry_date_for_new_batch = current_date + pd.Timedelta(days = shelf_life_days)

            # Câu lệnh này qua mỗi khi hàng đến sẽ ghi một từ điển vào inventory_batches, mỗi từ điển sẽ chứa 2 cặp key:item
            inventory_batches.append({
                'qty': int(incoming_goods),
                'exp': expiry_date_for_new_batch
            })
        




        if i > 0: # nếu i = 0 là dòng đầu tiên, đã được setup nên bỏ qua
            # Tồn kho thực tế đầu ngày sau khi trừ hàng hủy + hàng mới về
            # Được tính nhanh bằng tổng số lượng các lô hàng đang khả dụng
            



            # -------------------------------------------------------
            # KIỂM TRA SỐ LƯỢNG HÀNG TRONG KHO MỖI SÁNG
            # -------------------------------------------------------


            # Khách vào mua (Lấy sales của ngày hôm trước để trừ tồn kho lũy kế đầu ngày)
            last_sales = int(sales_array[i-1])


            # Tiến hành trừ hàng theo FEFO (Lô hạn gần nhất trừ trước)
            # Sắp xếp inventory_batches list theo thứ tự exp của mỗi dictionary
            inventory_batches = sorted(inventory_batches, key=lambda x: x ['exp'])

            # Tồn kho được tính vào đầu ngày trước khi bán, lấy tồn kho đầu ngày hôm qua trừ sales ngày hôm qua để có được tồn kho đầu ngày hôm nay
            remaining_sales = last_sales

            
            # Vòng lặp này sẽ xuất hàng theo batch để đáp ứng nhu cầu mỗi ngày
            for batch in inventory_batches:
                # Vòng lặp sẽ dừng khi nhu cầu được trừ đến 0
                if remaining_sales <= 0:
                    break
                # Nếu số lượng hàng trong lô đủ đáp ứng nhu cầu ngày i, tiến hành khấu trừ và nhu cầu ngày i bằng 0.
                # Vòng lặp tiếp theo quét thấy nhu cầu = 0 dừng vòng lặp
                if batch['qty'] >= remaining_sales:
                    batch['qty'] -= remaining_sales
                    remaining_sales = 0
                # Nếu số lượng hàng trong một lô không đủ đáp ứng nhu cầu, tiến hành khấu trừ toàn bộ số lượng còn trong lô vào nhu cầu.
                # Mỗi vòng lặp sẽ bốc một batch, nên vòng lặp tiếp theo sẽ bốc batch tiếp theo, vòng lặp chạy đến khi nhu cầu = 0 sẽ dừng vong lặp của ngày đó.
                else:
                    remaining_sales -= batch['qty']
                    batch['qty'] = 0


            # Làm sạch các lô đã bị cắn hết
            # Vì mỗi lô được lưu dưới dạng Dictionary ở trong inventory_batches List, vòng lặp for sẽ trừ mỗi batch cho đến khi bằng 0 và lưu số 0
            # b là mỗi Dictionary trong inventory_batches, lấy tất cả dictionary có b['qty'] > 0
            # Khi chạy vòng lặp, biến được tính toán sẽ được cập nhập luôn ở thư viện
            inventory_batches = [b for b in inventory_batches if b['qty'] > 0]

            # Ghi nhận giá trị on_hand chốt cuối ngày i
            on_hand[i] = sum([b['qty']for b in inventory_batches])
        else:
            # Ngày i = 0 đã được mặc định nền ở trên
            pass
            
            

        # Mặc định thừa hưởng lại mức ROP/TSL phẳng của ngày hôm trước
        # Vì last_rop đã được lưu, khi nào đặt hàng nữa mới cập nhập lại, nên rop_dynamic của ngày thường sẽ được ghi đi ghi lại theo last_rop cho đến ngày đặt hàng tiếp theo.
        rop_dynamic[i] = last_rop
        tsl_dynamic[i] = last_tsl

    
        # Inventory Position = On_hand + In Transit (Hàng đang trên đường về)
        in_transit = sum([qty for day, qty in arrival_date.items() if day > i]) # .items() biến các cặp key-value trong dictionary thành các cặp Tuple để dễ dàng duyệt qua (loop)
        # sum([qty for day, qty in arrival_date.items() if day > i]) hàm này hoạt động như:
        # in_transit = 0
        # for day, qty in arrival_date.items():
        #   if day > i: () đoạn code này để đảm bảo không cộng in_transit trong quá khứ
        #       in_transit += qty

        inventory_position[i] = on_hand[i] + in_transit




        # =======================================================
        # KIỂM TRA TRẠNG THÁI KHO CỦA NGÀY KIỂM KHO VÀ LÊN ĐƠN
        # =======================================================


        # LOGIC KIỂM KHO VÀ ĐẶT HÀNG 
        if group.loc[i, 'is_review_date']:



            # ----------------------------------------
            # TÍNH TOÁN LEAD TIME VÀ SỐ NGÀY BAO PHỦ 
            # ----------------------------------------


            # Mục đích của đoạn code này: Lọc tất cả các đơn hàng đã về kho trong cửa sổ 30 ngày gần nhất (từ ngày i - 30 đến ngày i)
            # Nên dùng khoảng thời gian ví dụ 1 tháng, 2 tháng để đánh giá năng lực của nhà cung cấp. Tránh dùng theo đơn vì tần suất đặt hàng của mỗi loại hàng sẽ khác nhau.
            # Ví dụ 30 đơn với mặt hàng A là 6 tháng nhưng với mặt hàng C có tần suất đặt hàng kém hơn có thể là 30 tháng.
            # Khoảng thời gian 30 tháng có thể cho là cũ để đánh giá năng lực của nhà cung cấp
            # Đoạn code này để ghi lại một list chứa lead time trong 60 ngày gần nhất
            recent_lead_times = [
                lt
                # vòng lặp được dùng để kiểm tra từng dữ liệu
                for day, lt_list in lead_time_history.items()
                if (i-60) <= day <= i # Chỉ lấy hàng về trong vòng 60 ngày qua
                # Cho i (stt) là ngày, vì ở df số ngày được viết liền nhau nên việc tính khoảng cách ngày sẽ rất chính xác.
                # Khi i được chuyển vào dictionary lead_time_history nó được bốc thẳng qua, dictionary lead_time_history sẽ tự sinh index khác
                for lt in lt_list
                # lt_list sau khi chuyển thành tuple sẽ ở dạng list vì câu lệnh ghi nhận list_time vào từ điển lead_time_history dùng .append().
                # Dùng vòng lặp thứ 2 để bốc lt_list lúc này ở dạng list[lt_list] ra khỏi dấu ngoặc [], ghi vào list recent_list_time để tính toán trung bình hoặc tổng. nếu recent_List_time = [[lt_list1], [lt_list2]] sẽ không thực hiện phép tính toán học được
            ]


            # -------------------------------------------------------
            # NHÁNH ĐÃ CÓ LEADTIME

            # Nhánh điều kiện 1: Nếu đã có dữ liệu leadtime
            if len(recent_lead_times) > 0:
                # Nhánh điều kiện 1.1: Nếu dữ liệu leadtime không đủ để tính toán
                if len(recent_lead_times) < 3:
                    current_mean = float(recent_lead_times[-1])
                    current_std = 0.00
                # Nhánh điều kiện 1.2: Nếu dữ liệu leadtime đủ để tính toán
                else:
                    current_mean = float(np.mean(recent_lead_times))
                    current_std = float(np.std(recent_lead_times))
                forecasted_lead_time = current_mean + current_std

                if shelf_life_days in [7, 14]:
                    tsl_coverage = int(np.ceil(forecasted_lead_time + R))
                else:
                    tsl_coverage = int(np.ceil(forecasted_lead_time + 2 * R))


            # -------------------------------------------------------
            # NHÁNH CHƯA CÓ LEADTIME

            # Nhánh điều kiện 2: Nếu chưa có dữ liệu leadtime
            # Lấy thẳng leadtime của ngày kiểm kho đầu tiên.
            else:
                if shelf_life_days in [7, 14]:
                    tsl_coverage = int(np.ceil(int(lead_time_array[first_review_idx]) + R))
                else:
                    tsl_coverage = int(np.ceil(int(lead_time_array[first_review_idx]) + 2 * R))

        


        # -------------------------------------------------------------
        # THIẾT LẬP NGÀY ĐẶT HÀNG ĐẦU TIÊN VÀ TÍNH TOÁN LƯỢNG HÀNG ĐẶT
        # -------------------------------------------------------------


        # LƯU Ý: Nếu đây là ĐƠN HÀNG ĐẦU TIÊN của hệ thống, ta ép nó phải đặt hàng
        # Để lấp đầy kho theo công thức bao phủ, bất kể tồn kho hiện tại là bao nhiêu.
        
            is_first_ever_order = (i == first_review_idx)

            if inventory_position[i] <= rop_dynamic[i] or is_first_ever_order:

                # -------------------------------------------------------
                # TÍNH TOÁN TSL, ROP CHO KÌ MỚI

                # Điểm bắt đầu của weekday_tsl_list
                start_point_weekday = i + 1
                # Điểm kết thúc của weekday_tsl_list
                end_point_weekday = min(start_point_weekday + 7, N)

                # Tạo list chứa đủ 7 weekday tsl tính từ ngày bắt đầu
                # Vì TSL cho mỗi weekday đã được tính từ 
                # Chúng ta dùng list TSL này để tính lặp lại nếu TSL coverage lớn hơn 7 ngày, để tránh lỗi nhìn vào dữ liệu tương lai
                weekday_tsl_list = demand_array[i + 1 : end_point_weekday]
                
               
                # Reset current_calculated_tsl để ghi lại giá trị mới
                current_calculated_tsl = 0
                current_calculated_rop = 0
                

                # Vì vòng lặp không thể chạy với số thực (float) nên phải làm tròn để có được số nguyên.
                r_days = int(np.floor(R))


                # Điều kiện này để rẽ nhánh tạo ra lớp phòng thủ, khi ở giai đoạn cuối của bảng dữ liệu nó sẽ xãy ra 2 trường hợp làm sập code, 2 điều kiện con bên dưới sẽ tạo ra lớp phòng thủ
                # Nếu N(= len(df)) < i + tsl_coverage thì lấy số ngày còn lại để chạy vòng lặp chứ không chạy hết số ngày tsl bao phủ


                # -------------------------------------------------------
                # NHÁNH TÍNH TOÁN TSL - ROP KHI DỮ LIỆU BỊ THIẾU
                len_list = len(weekday_tsl_list)
                if N < i + tsl_coverage:
                    remaindays = N - (i +1)

                    # Điều kiện này là lớp phòng thủ thứ 1 tránh sập code khi số ngày còn lại ít hơn cả r_days
                    # python nhặt một số trong range lớn hơn remaindays và tra cứu trong list tsl, ngày hôm đó không có trong list đoạn code sẽ bị sập
    
                    if remaindays <= r_days:
                        current_calculated_rop = 0
                        current_calculated_tsl = 0
                    
                    # Điều kiện này là lớp phòng thủ thứ 2 tránh sập code khi số ngày còn lại không đủ để lấy trọn vẹn 7 weekday tsl
                    # remaindays là chốt chặn, nếu dữ liệu ở giai đoạn cuối bảng không đủ để tsl_list lấy 7 weekday, remaindays sẽ bằng vừa khớp với tsl_list, làm cho việc tra cứu không bị sập 
                    else:
                        # Tính TSL - ROP cho mặt hàng có hxd 7/14 days
                        if shelf_life_days in [7,14]:

                            if len_list > 0:
                                for k in range(remaindays):
                                    current_calculated_rop += weekday_tsl_list[k % len_list]
                                if shelf_life_days == 14:
                                    current_calculated_rop = current_calculated_rop - 0.3 * weekday_tsl_list[0]
                                current_calculated_tsl = current_calculated_rop
                            else: 
                                current_calculated_rop = 0
                                current_calculated_tsl = 0
                        
                        # Tính TSL - ROP cho mặt hàng có hxd = 30 days
                        else: 
                            # Tính toán TSL
                            for k in range(remaindays):
                                # %7 để tính vòng lại list khi đi đến phần tử ở vị trí cuối.
                                future_weekday = k % 7
                                demand_of_day = weekday_tsl_list[future_weekday]
                                current_calculated_tsl += demand_of_day
                            
                            # Tính toán ROP
                            for k in range(r_days, remaindays):
                                future_weekday = k % 7
                                demand_of_day = weekday_tsl_list[future_weekday]
                                current_calculated_rop += demand_of_day             
                            current_calculated_rop = current_calculated_rop - 0.5 * weekday_tsl_list[r_days % 7]
                

                # -------------------------------------------------------
                # NHÁNH TÍNH TOÁN TSL - ROP KHI DỮ LIỆU BÌNH THƯỜNG

                # Trương hợp bình thường, i không ở giai đọa cuối của bảng dữ liệu
                else: 

                    # TÍNH TOÁN ROP - TSL CHO ITEM CÓ HXD 7/14 DAYS
                    if shelf_life_days in [7, 14]:
                        for k in range(tsl_coverage):
                            current_calculated_rop += weekday_tsl_list[k % len_list]
                        # Nếu shelf_life_days = 14 thì phải trừ đi 0.7 ngày dư vì làm tròn R từ 2.3 xuống 2
                        if shelf_life_days == 14: 
                            current_calculated_rop = current_calculated_rop - 0.3 * weekday_tsl_list[0]
                        else:
                            current_calculated_rop
                        # Nếu shelf_life_days = 7/14 thì rop và tsl bằng nhau
                        current_calculated_tsl = current_calculated_rop

                    # TÍNH TOÁN ROP - TSL CHO ITEM CÓ HXD 30 DAYS
                    else:
                        for k in range(tsl_coverage):
                            future_weekday = k % 7
                            demand_of_day = weekday_tsl_list[future_weekday]
                            current_calculated_tsl += demand_of_day

                        # Tính toán ROP
                        # tsl_coverage = R + R + L, rop_coverage = R + L nên điểm bắt đầu tính rop_coverage sẽ là R
                        for k in range (r_days, tsl_coverage):
                            future_weekday = k % 7
                            demand_of_day = weekday_tsl_list[future_weekday]
                            current_calculated_rop += demand_of_day
                        # r_days = round down R nên rop_coverage sẽ dư nữa ngày, nên ở đây trừ lượng dư nữa ngày để tránh dư thừa
                        current_calculated_rop = current_calculated_rop - 0.5 * weekday_tsl_list[r_days % 7]


                

                # -------------------------------------------------------
                # TÍNH TOÁN LƯỢNG HÀNG CẦN ĐẶT
                

                # ĐƠN ĐẦU TIÊN
                if is_first_ever_order:
                    # Ngày đầu tiên lên đơn, kho cần lượng hàng bằng đúng TSL bao phủ 9 ngày tới
                    order_qty[i] = current_calculated_tsl
                    # Ép đơn đầu tiên nhận 100% để tạo mốc nền tồn kho chuẩn
                    actual_received_qty = int(order_qty[i])
                
                # CÁC ĐƠN CÒN LẠI
                else: 
                    order_qty[i] = max(0, current_calculated_tsl - inventory_position[i])
                    # Lấy tỷ lệ đáp ứng của ngày lên đơn nhân với số lượng đặt
                    actual_received_qty = int(order_qty[i] * fill_rate_array[i]) 



                # -------------------------------------------------------
                # GHI NHẬN LỊH TRÌNH GIAO HÀNG
                # -------------------------------------------------------

                # Ghi nhận lịch xe tải giao hàng cập bến tương lai
                actual_lt = int(group.loc[i, 'assumed lead time'])
                delivery_day = i + actual_lt

                # Ghi nhận lượng hàng THỰC TẾ về kho   
                arrival_date[delivery_day] = actual_received_qty # Đoạn code này sẽ ghi actual_received_qty vào nhật ký arrival_date làm cho nó không còn trống nữa
                
                # Chỉ lưu lịch sử Lead time nếu xe tải thực sự có giao hàng (Tránh bùng đơn 0%)
                if actual_received_qty > 0: 
                    if delivery_day not in lead_time_history:
                        lead_time_history[delivery_day] = []
                    lead_time_history[delivery_day].append(actual_lt)


                # Câu lệnh này để lưu last_rop/last tsl cho đến ngày đặt hàng tiếp theo
                last_rop = current_calculated_rop
                last_tsl = current_calculated_tsl
                
                
    # Nạp ngược kết quả lại vào DataFrame để phân tích Excess/Shortage
    group['rop'] = rop_dynamic
    group['tsl'] = tsl_dynamic
    group['on_hand'] = on_hand
    group['inventory_position']= inventory_position
    group['order_qty'] = order_qty
    group['expired_qty'] = expired_log
    group['store_id'] = current_store
    group['item_id'] = current_item
    return group

# =====================================================================
# BƯỚC 3: KÍCH HOẠT GROUPBY CHẠY TRÊN TOÀN BỘ 26,000 DÒNG DỮ LIỆU
# =====================================================================

if df.index.names[0] is not None:
    df = df.reset_index()

df.columns = df.columns.str.strip()

# Pandas sẽ tự chia bảng tổng thành hàng trăm bảng nhỏ theo Store-Item,
# Ném vào hàm giả lập phía trên, chạy song song và gộp lại thành df_final
df_final= df.groupby(['store_id', 'item_id'], as_index=True, group_keys= False).apply(calculate_by_group)

df_final = df_final.reset_index(drop=True)
