echo "Init tests ..."
echo "Clear old results..."
rm result_text.csv
rm result_image.csv
echo "Titre;Statut;Algorithme;Taille initial;Taille après compression;Taille des données pour décodage;Taux de compression sans les données pour décodage;Taux de compression avec les données de décodage;Taille avec utilisation d'un dictionnaire;Taille du dictionnaire;Taux de compression sans le dictionnaire;Taille de compression avec le dictionnaire;Temps" > result_text.csv
echo "Titre;Statut;Algorithme;Taille initial;Taille après compression;Taille des données pour décodage;Taux de compression sans les données pour décodage;Taux de compression avec les données de décodage;Taille avec utilisation d'un dictionnaire;Taille du dictionnaire;Taux de compression sans le dictionnaire;Taille de compression avec le dictionnaire;Temps" > result_image.csv
echo "Running tester ..."
echo "-------------------Text encoding--------------------"
for file in ./dataset/text_files/*
do
    echo "Compressing ... ""$file"

    #Add -d to go in debug mod
    echo "Message ..."
    python main.py -t -M -ALL "$file"
    echo "Unicode ..."
    python main.py -t -Unicode -ALL "$file"
done

echo "Compressing random ..."
python main.py -t -RAND -ALL 40
python main.py -t -RAND -ALL 100
python main.py -t -RAND -ALL 240
python main.py -t -RAND -ALL 600
python main.py -t -RAND -ALL 1200
python main.py -t -RAND -ALL 3000

echo "-------------------Image encoding-------------------"
for file in ./dataset/image_files/*
do
    echo "Compressing ... ""$file"

    #Add -d to go in debug mod
    echo "GRAY ..."
    python main.py -i -GRAY -ALL "$file"
    echo "RGB ..."
    python main.py -i -RGB -ALL "$file"
done
echo "DONE"