# Phan cong nhom 3 nguoi - Lab 7

Tai lieu nay dung de chia viec ro rang cho nhom 3 nguoi, voi ban lam nhom truong.
Muc tieu la:
- Khong bi chong cheo viec
- Biet viec nao phai lam truoc viec nao
- Co dau ra ro rang de ghep vao `report/REPORT_NHOM.md`

---

## 1. Tong quan cong viec nhom

Phan nhom cua bai lab gom 4 khoi viec chinh:

1. Chon pham vi tai lieu trong chu de K3
2. Thu thap va lam sach corpus
3. Thiet ke benchmark 5 cau hoi + gold answers
4. Chay benchmark, so sanh chien luoc, viet bao cao nhom

Ngoai ra, moi thanh vien van co phan code ca nhan rieng trong `src/` va `report/REPORT_CANHAN_2A202601874.md`, nhung file nay khong nam trong pham vi phan cong nhom.

---

## 2. Phan cong theo tung nguoi

### Thanh vien 1: Ban - Nhom truong

Ban la nguoi:
- Chot pham vi de tai
- Chot tieu chuan dau ra
- Tong hop ket qua
- Kiem tra tinh dong bo giua data, benchmark, va report

Cong viec cu the:

1. Chot pham vi corpus
   - Chon 1 pham vi hep trong chu de K3, vi du:
     - dang ky mon + hoc phi
     - thu vien + ky tuc xa
     - hoc bong + quy dinh hoc vu
   - Khong nen om qua rong ngay tu dau.

2. Chot tieu chuan metadata
   - Bat buoc:
     - `doc_id`
     - `title`
     - `source_url`
     - `retrieved_at`
     - `document_version`
     - `audience`
   - Nen them:
     - `category`
     - `department`
     - `language`

3. Chot 5 benchmark questions
   - Dam bao da dang:
     - 1 cau ve dinh nghia/quy dinh
     - 1 cau ve quy trinh
     - 1 cau ve thoi han/dieu kien
     - 1 cau can `metadata_filter`
     - 1 cau tong hop/so sanh
   - Viet gold answer ro rang, co the kiem chung.

4. Phan cong chien luoc cho tung nguoi
   - Moi nguoi phai thu 1 chien luoc khac nhau
   - Quy uoc truoc:
     - nguoi A: baseline hoac `SentenceChunker`
     - nguoi B: `RecursiveChunker`
     - nguoi C: custom chunker theo heading/section hoac `FixedSizeChunker` tinh chinh

5. Tong hop ket qua va viet report
   - Gom:
     - danh sach tai lieu
     - metadata schema
     - benchmark questions
     - ket qua top-3 retrieval
     - failure cases
     - bai hoc rut ra

6. Kiem tra cuoi
   - Kiem tra xem:
     - 5 cau hoi co khop nhau giua `REPORT_NHOM.md` va `REPORT_CANHAN_2A202601874.md`
     - ngay / version / source_url co day du
     - moi thanh vien da co du lieu de lam phan cua minh

---

### Thanh vien 2: Phu trach data collection

Nguoi nay chiu trach nhiem toan bo pipeline du lieu.

Cong viec cu the:

1. Tim nguon tai lieu
   - Chi lay nguon cong khai hoac duoc phep chia se
   - Uu tien:
     - trang chinh thuc cua truong
     - quy dinh
     - FAQ
     - huong dan dich vu

2. Tai va loc tai lieu
   - Lay 5-10 tai lieu
   - Moi tai lieu phai nam trong pham vi da chot
   - Bo:
     - menu
     - footer
     - banner
     - noi dung khong lien quan

3. Chuan hoa ve `.md` hoac `.txt`
   - Moi file chi chua 1 tai lieu nguon
   - Neu la PDF/web, chuyen sang text sach
   - Dat ten file ro rang, khong trung lap

4. Ghi front matter metadata
   - Moi file `.md` can co:
     - `doc_id`
     - `title`
     - `source_url`
     - `retrieved_at`
     - `document_version`
     - `audience`
     - it nhat 1 field phu

5. Tao `sources.csv`
   - Moi dong 1 tai lieu
   - Dam bao:
     - `file_path` dung
     - `doc_id` khong trung
     - metadata khop voi file

6. Kiem tra corpus truoc khi ban giao
   - Dam bao:
     - file co the doc duoc
     - khong thieu metadata
     - khong co thong tin nhay cam
     - co du noi dung de tra loi benchmark

7. Ban giao cho ban
   - Gui:
     - danh sach file
     - `sources.csv`
     - metadata tieu bieu
     - ghi chu file nao manh / yeu cho retrieval

---

### Thanh vien 3: Phu trach retrieval strategy va benchmark

Nguoi nay chiu trach nhiem phan so sanh ket qua truy xuat.

Cong viec cu the:

1. Chay baseline
   - Dung `ChunkingStrategyComparator().compare()`
   - Chay tren 2-3 tai lieu mau
   - Ghi lai:
     - so chunk
     - do dai trung binh
     - chunk co giu duoc ngu canh khong

2. Chon chien luoc rieng
   - Chon 1 trong cac huong:
     - `SentenceChunker`
     - `RecursiveChunker`
     - custom chunker theo heading/section
   - Neu co the, thu them 1 bo tham so khac de so sanh.

3. Chuan bi benchmark run
   - Dung dung 5 cau hoi da chot
   - Chay cung 1 corpus
   - Neu can so sanh nghiem tuc, dat `EMBEDDING_PROVIDER=local`

4. Chay retrieval va ghi log
   - Cho moi cau hoi, ghi:
     - top-1
     - top-2
     - top-3
     - score
     - co relevant khong
     - agent tra loi dung khong

5. Lam failure analysis
   - Tim it nhat 1 truong hop that bai
   - Neu ro nguyen nhan:
     - chunk qua nho
     - chunk qua lon
     - metadata thieu
     - filter qua chat
     - cau hoi mo ho

6. Tong hop so sanh
   - So sanh:
     - chien luoc nao tot hon
     - cau nao chien luoc A tot hon B
     - metadata filter co giup gi khong

7. Ban giao cho ban
   - Gui:
     - bang benchmark
     - nhan xet ve chien luoc
     - failure case
     - goi y bai hoc rut ra

---

## 3. Luong cong viec tung buoc va phu thuoc

Day la thu tu de lam viec de tranh bi tac.

### Buoc 1: Chot pham vi

Lam gi:
- Ban chot 1 pham vi hep trong K3
- Noi ro nhom se lam ve gi

Phu thuoc:
- Khong phu thuoc gi

Output:
- 1 cau mo ta pham vi
- danh sach chu de con duoc phep

---

### Buoc 2: Tim nguon tai lieu

Lam gi:
- Thanh vien 2 tim 5-10 nguon cong khai
- Loc nguon theo pham vi da chot

Phu thuoc:
- Phai xong Buoc 1

Output:
- danh sach URL
- file source ban dau

---

### Buoc 3: Lam sach va chuan hoa file

Lam gi:
- Thanh vien 2 chuyen thanh `.md` hoac `.txt`
- Bo phan thua
- Ghi front matter day du

Phu thuoc:
- Phai xong Buoc 2

Output:
- 5-10 file tai lieu
- metadata day du

---

### Buoc 4: Tao `sources.csv`

Lam gi:
- Thanh vien 2 lap file `sources.csv`
- Ban kiem tra lai

Phu thuoc:
- Phai xong Buoc 3

Output:
- `sources.csv` khop voi file

---

### Buoc 5: Kiem tra corpus va nhoan pham vi benchmark

Lam gi:
- Ban va thanh vien 3 doc corpus
- Chot xem tai lieu nao du de ra cau hoi
- Chot 5 benchmark questions

Phu thuoc:
- Phai xong Buoc 3 va Buoc 4

Output:
- 5 cau hoi
- 5 gold answers

---

### Buoc 6: Chon chien luoc cho tung nguoi

Lam gi:
- Moi nguoi chon 1 strategy rieng
- Noi ro ly do chon

Phu thuoc:
- Phai xong Buoc 5
- Nen co corpus on dinh truoc

Output:
- phan cong chien luoc cu the

---

### Buoc 7: Chay baseline va benchmark

Lam gi:
- Thanh vien 3 chay baseline
- Moi nguoi chay 5 cau hoi benchmark tren chien luoc cua minh

Phu thuoc:
- Phai xong Buoc 5 va Buoc 6

Output:
- bang ket qua top-3
- score
- agent answer

---

### Buoc 8: So sanh va phan tich

Lam gi:
- Ca nhom xem top-3, score, va agent answer
- Tim case tot va case that bai

Phu thuoc:
- Phai xong Buoc 7

Output:
- phan tich so sanh
- failure case
- nhan xet metadata filter

---

### Buoc 9: Viet report nhom

Lam gi:
- Ban tong hop toan bo ket qua
- Dien vao `report/REPORT_NHOM.md`

Phu thuoc:
- Phai xong Buoc 1 den Buoc 8

Output:
- `REPORT_NHOM.md` hoan chinh

---

## 4. So do phu thuoc cong viec

```text
Buoc 1: Chot pham vi
   |
   v
Buoc 2: Tim nguon tai lieu  -----> Buoc 3: Lam sach va chuan hoa file
   |                                         |
   v                                         v
Buoc 4: Tao sources.csv  --------->  Buoc 5: Chot benchmark questions
                                             |
                                             v
                                  Buoc 6: Chon chien luoc cho tung nguoi
                                             |
                                             v
                                  Buoc 7: Chay baseline va benchmark
                                             |
                                             v
                                  Buoc 8: So sanh va phan tich
                                             |
                                             v
                                  Buoc 9: Viet report nhom
```

---

## 5. Checklist theo nguoi

### Ban
- [ ] Chot pham vi
- [ ] Chot metadata schema
- [ ] Chot 5 benchmark questions
- [ ] Chot phan cong chien luoc
- [ ] Tong hop ket qua va viet report

### Thanh vien 2
- [ ] Tim 5-10 tai lieu
- [ ] Lam sach file `.md` / `.txt`
- [ ] Them front matter metadata
- [ ] Tao `sources.csv`
- [ ] Ban giao corpus da kiem tra

### Thanh vien 3
- [ ] Chay baseline
- [ ] Chon strategy rieng
- [ ] Chay 5 benchmark questions
- [ ] Ghi top-3, score, agent answer
- [ ] Viet failure analysis

---

## 6. Thu tu lam viec de nhom khong bi tre

Neu muon lam nhanh va dung thu tu, nen di theo trinh tu sau:

1. Ban chot pham vi
2. Thanh vien 2 lay va lam sach tai lieu
3. Ban + thanh vien 3 chot benchmark questions
4. Thanh vien 3 chay baseline va chuan bi template benchmark
5. Moi nguoi chay strategy rieng tren cung benchmark
6. Ban tong hop ket qua
7. Ca nhom soat lai report truoc khi nop

---

## 7. Ghi chu quan trong

- Mọi nguoi phai dung cung mot bo 5 benchmark questions
- Moi thanh vien phai co 1 chien luoc retrieval rieng de so sanh
- It nhat 1 cau hoi phai can metadata filter
- Data phai cong khai, khong duoc co thong tin nhay cam
- Neu corpus chua on, khong nen chay benchmark ngay vi ket qua se khong y nghia
