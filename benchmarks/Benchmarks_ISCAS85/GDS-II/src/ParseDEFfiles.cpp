#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>
#include <map>
#include <stdexcept>

// Struct to have cell information
struct CellStruct
{
    std::string CellID;
    std::string CellType;
    float X_Loc;
    float Y_Loc;
    std::string CellOrientation;
};
// struct to have the die information
struct DieStruct
{
    std::string DesignName;
    float DieXSize;
    float DieYSize;
    float DesignUnit;
} DieDetail;

// Struct to be returned
struct DEF_INFO
{
    std::map<std::string, CellStruct> MapCells;
    std::map<std::string, DieStruct> DieInfo;
};

CellStruct Vector2Struct(std::vector<std::string> EachLine)
{
    CellStruct cells;
    int offset = 0;
    if (EachLine.size() == 13)
    {
        offset = 3;
    } // This if statment is for the logic cells
    else if (EachLine.size() == 10)
    {
        offset = 0;
    } // This if statement is for the fillers/endcaps/tapcells
    else
    {
        std::cout << "provide the correct length of word for the cell definition of *.DEF file";
        throw std::invalid_argument("check the length of each cell line definition in the *.DEF file; it is not logic cell or filler/endcap/tapcell cell");
    }

    cells.CellID = EachLine[1];
    cells.CellType = EachLine[2];
    cells.X_Loc = std::stof(EachLine[6 + offset]);
    cells.Y_Loc = std::stof(EachLine[7 + offset]);
    cells.CellOrientation = EachLine[9 + offset];

    return cells;
};

DEF_INFO ParseDEFfiles(const std::string &filePath)
{
    DEF_INFO def_info;
    std::ifstream file(filePath);
    if (!file)
    {
        std::cerr << "Failed to open the file." << std::endl;
        return def_info;
    }

    std::string line;
    int componnents_flag = 0;
    int design_name_flag = 0;
    // std::map<std::string, std::vector<std::string>> map_gate;
    // std::map<std::string, std::vector<std::string>> map_misc;

    std::map<std::string, CellStruct> MapCells;
    std::map<std::string, DieStruct> DieInfo;

    while (std::getline(file, line))
    {

        if (!line.empty())
        {
            std::stringstream lineSstrm(line);
            std::vector<std::string> lineVect;
            std::string word;
            while (lineSstrm >> word)
            {
                lineVect.push_back(word);
            }
            // extract the name
            if (lineVect[0] == "DESIGN" && lineVect.size() > 0 && design_name_flag == 0)
            {
                DieDetail.DesignName = lineVect[1];
                design_name_flag = 1;
            }
            // end of extracting the name

            // retriving the DieArea size
            if (lineVect[0] == "DIEAREA" && lineVect.size() > 0)
            {
                DieDetail.DieXSize = std::stof(lineVect[6]);
                DieDetail.DieYSize = std::stof(lineVect[7]);
            }
            // retrieving the Die size Unit
            if (lineVect[0] == "UNITS" && lineVect.size() > 0)
            {
                DieDetail.DesignUnit = std::stof(lineVect[3]);
            }

            // extract the name of the gates, and location
            if (lineVect[0] == "COMPONENTS" && lineVect.size() > 1)
                componnents_flag = 1;
            if (lineVect[0] == "END" && lineVect[1] == "COMPONENTS")
                componnents_flag = 0;
            if (componnents_flag == 1 && lineVect[0] != "COMPONENTS")
            {

                if (lineVect.size() == 10)
                {
                    // push the gate related details to the MapCells
                    MapCells[lineVect[1]] = Vector2Struct(lineVect);
                }

                if (lineVect.size() == 13)
                {
                    // push the miscellanious cells (fillers, endcaps, tapwells) to the the MapCells
                    MapCells[lineVect[1]] = Vector2Struct(lineVect);
                }
            }
        }
    }
    DieInfo["INFO"] = DieDetail;

    file.close(); // Close the file                                                                                                                                                                                                                                                                                                                // Uncomment for the testing

    /*
    std::cout << "MapCells[\"g929\"] " << MapCells["g929"].CellID << " " << MapCells["g929"].CellType << " " << MapCells["g929"].CellOrientation << " " << MapCells["g929"].X_Loc << " " << MapCells["g929"].Y_Loc << "\n";                                                                                     // for testing only
    std::cout << "MapCells[\"g891\"] " << MapCells["g891"].CellID << " " << MapCells["g891"].CellType << " " << MapCells["g891"].CellOrientation << " " << MapCells["g891"].X_Loc << " " << MapCells["g891"].Y_Loc << "\n";                                                                                     // for testing only
    std::cout << "MapCells[\"FILLER_impl1_0_223\"] " << MapCells["FILLER_impl1_0_223"].CellID << " " << MapCells["FILLER_impl1_0_223"].CellType << " " << MapCells["FILLER_impl1_0_223"].CellOrientation << " " << MapCells["FILLER_impl1_0_223"].X_Loc << " " << MapCells["FILLER_impl1_0_223"].Y_Loc << "\n"; // for testing only
    std::cout << "Die information " << DieInfo["INFO"].DesignName << " " << DieInfo["INFO"].DieYSize << "\n";
    */
    def_info.MapCells = MapCells;
    def_info.DieInfo = DieInfo;

    return def_info;
}

int main()
{
    DEF_INFO result = ParseDEFfiles("../asset/design.def");

    std::map<std::string, CellStruct> mapCells = result.MapCells;
    std::map<std::string, DieStruct> dieInfo = result.DieInfo;

    // Use the mapCells and dieInfo variables as needed
    std::cout << "MapCells[\"g929\"] " << result.MapCells["g929"].CellID << " " << result.MapCells["g929"].CellType << " " << result.MapCells["g929"].CellOrientation << " " << result.MapCells["g929"].X_Loc << " " << result.MapCells["g929"].Y_Loc << "\n";                                                                                     // for testing only
    std::cout << "MapCells[\"g891\"] " << result.MapCells["g891"].CellID << " " << result.MapCells["g891"].CellType << " " << result.MapCells["g891"].CellOrientation << " " << result.MapCells["g891"].X_Loc << " " << result.MapCells["g891"].Y_Loc << "\n";                                                                                     // for testing only
    std::cout << "MapCells[\"FILLER_impl1_0_223\"] " << result.MapCells["FILLER_impl1_0_223"].CellID << " " << result.MapCells["FILLER_impl1_0_223"].CellType << " " << result.MapCells["FILLER_impl1_0_223"].CellOrientation << " " << result.MapCells["FILLER_impl1_0_223"].X_Loc << " " << result.MapCells["FILLER_impl1_0_223"].Y_Loc << "\n"; // for testing only
    std::cout << "Die information " << result.DieInfo["INFO"].DesignName << " " << result.DieInfo["INFO"].DieYSize << "\n";
    return 0;
}
