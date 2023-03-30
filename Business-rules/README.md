# Business rules voor recommendation engine
Door: Mark Willemse  
Studentnummer: 1828116

## Filters
Deze code voert twee filters uit op de data uit de relationele database om zo recommendations te kunnen geven. deze slaat hij op in twee tabellen
 - rec_brand
 - rec_brand_others

 ### rec_brand (content)
 In deze tabel komt de volgende data te staan:
 1. product_id
 2. product_id's van producten met dezelfde brand

 Dus hij pakt de producten die dezelfde brand hebben als het gegeven of het product dat bijvoorbeeld bekeken wordt  
 voorbeelden:     

    Meer producten van hetzelfde merk als dat van id: 39949:
    ids: [20142]

    Meer producten van hetzelfde merk als dat van id: 46324-3pack:
    ids: [33285, 46324]

    Meer producten van hetzelfde merk als dat van id: 40318-wit:
    ids: [40318-bruin, 40318-groen, 40318-zwart]

    Meer producten van hetzelfde merk als dat van id: 45983:
    ids: [45987, 45986, 45988, 45985, 45984]

    Meer producten van hetzelfde merk als dat van id: 45077:
    ids: [45138]

data uit database:  
![exampledata rec_brand](/images/rec_brand.png)


### rec_brand_others (collaborative)
In deze tabel komt de volgende data te staan:
1. brand
2. brand die anderen bekeken   

Hij pakt voor het gegeven brand(of natuurlijk de brand die bekeken wordt) anderen brands die in dezelfde sessie door anderen zijn gekocht of bekeken. 
voorbeelden:  

    Mensen die van Pro Garden kochten, kochten ook van merken als [Red Bull, Schwarzkopf]

    Mensen die van Nouka kochten, kochten ook van merken als [Nivea]

    Mensen die van Home Basics kochten, kochten ook van merken als [Predictor, Wella, Vivess, Op is Op, Amando, Schwarzkopf, Giorgio Beverly Hills, My Little Pony, Gillette, Disney, Zwitsal]

    Mensen die van Op is Op kochten, kochten ook van merken als [Andrelon, Mullrose]

    Mensen die van Calgon kochten, kochten ook van merken als [W7, Star Bright, Dreft]
data uit database:  
![example rec_brand_others](/images/rec_brand_others.png)
