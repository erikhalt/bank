from person import *
import unittest

class PersonTEst(unittest.TestCase):
    def test_When_creating_person_name_and_personnumber_should_be_set(self):
        #Arrange
        name = "Erik"
        PersonNumber = "9803282418"

        #Set
        sut = Person(name,PersonNumber)

        #Assert
        self.assertEqual(name,sut.Name)
        self.assertEqual(PersonNumber,sut.PersonNumber)



class PersonRegisterTest(unittest.TestCase):
    def test_when_fetching_person_correct_person_should_be_returned(self):
        person1 = Person("Erik","1123123-123")
        person2 = Person("Erik","1654623-553")

        sut = PersonRegister()
        sut.add(person1)
        sut.add(person2)

        result = sut.getPerson("84684684-948")

        self.assertEqual("Finns inte",result)

if __name__ is "__main__":
    unittest.main()
